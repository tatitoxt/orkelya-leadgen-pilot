#!/usr/bin/env python3
"""Run a bounded, $0 OSM directory-discovery pilot for Orkelya.

The script reads authorized local CRM and suppression history, performs exact
and normalized deduplication, and exports remaining records as research-only
candidates. It never sends or drafts messages and does not visit candidate sites.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from openpyxl import load_workbook

from leadgen import get_vertical, run_pipeline
from leadgen.export import write_outputs
from leadgen.suppression import norm


def _domain(value: str | None) -> str:
    if not value:
        return ""
    raw = value.strip().lower()
    if not raw:
        return ""
    host = urlparse(raw if "://" in raw else f"https://{raw}").hostname or ""
    return host.removeprefix("www.")


def _digits(value: str | None) -> str:
    return re.sub(r"\D", "", value or "")


def _read_workbook(path: Path) -> tuple[set[str], set[str], set[str], set[str]]:
    wb = load_workbook(path, read_only=True, data_only=True)
    if "Prospectos" not in wb.sheetnames:
        raise ValueError("Workbook has no 'Prospectos' sheet; refusing to run without CRM dedupe.")
    ws = wb["Prospectos"]
    rows = ws.iter_rows(values_only=True)
    headers = [str(v or "").strip() for v in next(rows, ())]
    positions = {h: i for i, h in enumerate(headers)}
    if "Empresa" not in positions:
        raise ValueError("Workbook has no 'Empresa' column; refusing to run without CRM dedupe.")

    names: set[str] = set()
    domains: set[str] = set()
    phones: set[str] = set()
    emails: set[str] = set()
    for row in rows:
        def cell(key: str) -> str:
            i = positions.get(key)
            return str(row[i] or "").strip() if i is not None and i < len(row) else ""

        if cell("Empresa"):
            names.add(norm(cell("Empresa")))
        for key, bucket, fn in (
            ("Sitio web de empresa", domains, _domain),
            ("Redes sociales públicas", domains, _domain),
            ("Teléfono público", phones, _digits),
            ("Email público", emails, lambda v: v.lower()),
        ):
            value = fn(cell(key))
            if value:
                bucket.add(value)
    wb.close()
    return names, domains, phones, emails


def _read_history(paths: list[Path]) -> str:
    pieces = []
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"Required deduplication source is missing: {path}")
        pieces.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(pieces)


def _matches_history(rec: dict, history: str) -> bool:
    # A match suppresses a candidate; an unmatched candidate is still labeled
    # partial because these Markdown logs cannot establish inbox/social state.
    haystack = norm(history)
    identifiers = [
        norm(rec.get("name", "")),
        _domain(rec.get("website")),
        (rec.get("email") or "").strip().lower(),
        _digits(rec.get("phone")),
    ]
    return any(len(key) >= 7 and key in haystack for key in identifiers if key)


def _matches_workbook(rec: dict, known: tuple[set[str], set[str], set[str], set[str]]) -> bool:
    names, domains, phones, emails = known
    return any(
        (
            norm(rec.get("name", "")) in names,
            bool(_domain(rec.get("website")) and _domain(rec.get("website")) in domains),
            bool(_digits(rec.get("phone")) and _digits(rec.get("phone")) in phones),
            bool((rec.get("email") or "").strip().lower() in emails and rec.get("email")),
        )
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--market", required=True, help='Specific geocodable place, e.g. "Buenos Aires, Argentina"')
    ap.add_argument("--workbook", required=True, type=Path, help="Current authorized Paperclip CRM workbook")
    ap.add_argument("--pipeline", required=True, type=Path, help="Canonical PIPELINE-OUTREACH.md")
    ap.add_argument("--control", required=True, type=Path, help="Canonical CONTROL-OUTREACH.md")
    ap.add_argument("--out", required=True, type=Path, help="Output file stem outside the source repository")
    ap.add_argument("--limit", type=int, default=50, help="Maximum candidates exported after the bounded market query; default 50")
    args = ap.parse_args()
    if args.limit < 1 or args.limit > 100:
        ap.error("--limit must be between 1 and 100 for this pilot")

    known = _read_workbook(args.workbook)
    history = _read_history([args.pipeline, args.control])
    vertical = get_vertical("orkelya_logistics")
    observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    records = run_pipeline(
        vertical,
        args.market,
        sources=("osm",),
        limit=args.limit,
        enrich=False,
        enrich_cap=0,
        out_stem=None,
        exclude_names=known[0],
        log=print,
    )

    records = records[: args.limit]
    exported = []
    workbook_dupes = history_dupes = 0
    for rec in records:
        if _matches_workbook(rec, known):
            workbook_dupes += 1
            continue
        if _matches_history(rec, history):
            history_dupes += 1
            continue
        rec["observed_at_utc"] = observed_at
        rec["source_updated_at"] = "Unknown; source collector does not expose edit timestamp"
        rec["research_status"] = "UNQUALIFIED DIRECTORY CANDIDATE — NOT CONTACTABLE"
        rec["dedupe_status"] = (
            "PARTIAL — checked current workbook, PIPELINE-OUTREACH.md, and "
            "CONTROL-OUTREACH.md; inbox/social/other task history not verified"
        )
        rec["why"] = (
            "OSM directory record only; current need and buyer are unverified; "
            "dedupe is partial; do not contact"
        )
        rec["tier"] = "C"
        rec["score"] = 0
        exported.append(rec)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    paths = write_outputs(exported, vertical.columns, str(args.out), log=print) if exported else ()
    print(
        "PILOT SUMMARY: "
        f"fetched_after_engine_dedupe={len(records)}; "
        f"excluded_workbook={workbook_dupes}; excluded_history={history_dupes}; "
        f"research_only_candidates={len(exported)}; contacts_sent=0; spend_usd=0"
    )
    if paths:
        print(f"CSV={paths[0]}\nXLSX={paths[1]}")
    else:
        print("No export created: no unqualified candidates survived the local dedupe gates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
