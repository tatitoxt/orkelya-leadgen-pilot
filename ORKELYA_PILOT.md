# Orkelya local prospecting pilot

## Decision

Use this repository as a local, $0 directory-discovery assistant, not as an
autonomous sales agent. The initial vertical queries OpenStreetMap only for
named logistics, transport, and warehouse records. It performs no website
enrichment, email verification, message drafting, or sending. Every result is
marked tier C, unqualified, and not contactable.

The run reads the current authorized CRM workbook and the canonical
`PIPELINE-OUTREACH.md` and `CONTROL-OUTREACH.md` locally. It excludes exact
company-name matches, public email/phone/domain matches from the workbook, and
normalized name/contact matches in the two Markdown logs. Remaining rows are
still labeled `DEDUPE PARTIAL`: the script cannot establish that inboxes,
Facebook/Instagram, or every Paperclip artifact were checked. It also records
the local observation time separately from the source record's update time,
which remains `Unknown` because this source path does not provide that date.

## Run it

From this repository, after installing the project into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python scripts/run_orkelya_pilot.py \
  --market "Buenos Aires, Argentina" \
  --workbook "/path/to/505_Prospectos_Pipeline_Outreach_Paperclip_2026-10-20.xlsx" \
  --pipeline "/path/to/PIPELINE-OUTREACH.md" \
  --control "/path/to/CONTROL-OUTREACH.md" \
  --out "/tmp/orkelya-logistics-candidates-YYYY-MM-DD" \
  --limit 50
```

Use a narrow, named market. `--limit` caps exported rows after the bounded
market query, not the number of records received from Overpass. Outputs go to
the chosen directory and should not be committed. OSM is licensed under ODbL;
retain attribution and follow the source terms if redistributing data. This
pilot is for internal research only.

## Why not install every scraper

| Option | Decision | Reason |
| --- | --- | --- |
| Dukotah/leadgen | Selected for pilot | Python, MIT engine, multiple free public/open-data sources, local CSV/XLSX export. We restrict first run to OSM and one vertical. |
| LeadForge | Do not deploy into this pipeline yet | Stronger data lineage, suppression, and scoring; MIT. Its default discovery path is an OSS Maps scraper, and it has optional browser/NER/model dependencies. Review individual source terms and add it only after a clean, small geography-specific audit. |
| Scrapy / Crawlee / Crawl4AI | Do not install alone | Crawl engines without a defined compliant data source, dedupe model, and buying-signal logic. Add only for a specific permitted source. |
| ScrapeGraphAI | Do not install | Extractor rather than discovery/source-of-record; model calls or local Ollama add cost/compute, and Orkelya has no free model runtime budget allocated. |

No repository can safely or reliably scrape “the whole internet.” Open sources
are incomplete, change over time, and rarely show an actual buying signal. The
pilot will not count directory records toward the 150/day contact target. That
target cannot be reached by sending 150 unqualified cold messages; the system
should measure qualified candidates and completed, permitted individual
contacts separately.

## First verified run — 2026-10-22

Market: Buenos Aires, Argentina. Source: OpenStreetMap via the repository's OSM
collector. The engine returned 4 named records; local dedupe excluded 1 against
the outreach history and 3 were exported for manual research:

| Record | OSM source | Classification |
| --- | --- | --- |
| Logística Olavarría | https://www.openstreetmap.org/node/6355581663 | Tier C, score 0, unqualified, not contactable |
| SAF Depósito Fiscal | https://www.openstreetmap.org/way/1023620318 | Tier C, score 0, unqualified, not contactable |
| Tornus Logistica | https://www.openstreetmap.org/relation/16665373 | Tier C, score 0, unqualified, not contactable |

All 3 have partial dedupe only: the 505-name workbook and the two canonical
outreach logs were checked, but the complete Paperclip history, inboxes, and
social channels were not. OSM's record update date is not exposed by this
collector. No company site was visited, no buying signal or decision-maker was
verified, no lead was promoted, no contact was drafted or sent, and spend was
$0. Files were written outside the repository to
`/tmp/orkelya-logistics-pilot-2026-10-22/`.

## Paperclip status and gate

Live status verified 2026-10-22 at 15:54 ART. The Decisions page shows five
attention items. ORK-68 is `Blocked`; Paperclip reports that the agent needs
attention after two automatic recovery attempts failed. The routine
**Revisión operativa de Decisions y bloqueos** is paused, as are Tier 1 lead
research, continuous prospecting, and commercial follow-ups. The weekly
Obsidian routine is active but has no recorded runs. No continuous work is
verified.

COO still has the `Orkelya runner SSH` environment override selected and
sandbox bypass off. That selection and the successful runtime/chat probe did
not make a real task work: the work test failed before command execution with
`bwrap: setting up uid map: Permission denied`. A direct SSH attempt from the
current Mac session reached the host but failed authentication with
`Permission denied (publickey)`. No key was inspected or exposed. ORK-68 now
contains an actionable host diagnosis: check distro/kernel, AppArmor bwrap
profile and DENIED audit events; use the profile compatible with the installed
Ubuntu release; test as `paperclip-runner`; preserve AppArmor, seccomp, and
sandbox enforcement. The OS version and audit evidence remain unknown, so the
AppArmor cause is a hypothesis, not a confirmed finding.

Do not resolve ORK-68 or retry dependent work until an administrator confirms
a successful `bwrap` health check with AppArmor/seccomp still active, then
verifies one harmless Paperclip work task via COO's SSH override. Re-enable
dependent routines one at a time only after end-to-end task success. Keep this
failure in the single canonical issue; do not create another recovery for the
same root cause.

## Files and data handling

- `leadgen/verticals/orkelya_logistics.py`: conservative logistics vertical.
- `scripts/run_orkelya_pilot.py`: local CRM/history dedupe and safe export.
- Generated CSV/XLSX files belong outside the repository. The repository
  `.gitignore` also excludes generated lead records.
- Do not connect this pilot to Paperclip until the task-run path works and the
  output has been reviewed for dedupe completeness and source quality.

## Additional runtime diagnosis — 2026-10-22 16:00 ART

A Paperclip environment test for `Commercial Intelligence` also failed with
`Couldn't connect`. The responsible user's connection was selected and web
search remained disabled. Details show managed Codex ACP credentials staged in
`/tmp/paperclip-ai-…/provider`; the CLI hello probe reported Codex refusing to
create helper binaries under `/tmp`. I tried enabling web search, but Paperclip
rejected saving the change because the AI connection failed validation; I
reverted the unsaved setting. I did not change the agent's Codex account,
execution engine, sandbox, or environment.

Paperclip upstream issue 16337 contains the same temporary-home warning. Its
Linux follow-up says this warning may not be the fatal cause: the hello probe
passed with an existing Git checkout or `--skip-git-repo-check`. Our `/app`
working directory was called valid, but its Git status and the full fatal
provider error were not shown, so this remains a hypothesis. An operator should
inspect the complete environment-test logs and confirm Paperclip build, working
directory, and Git status; prefer an isolated runner-owned Git checkout or a
supported probe configuration. Do not apply the skip-check option generally
without a security review. This is separate from ORK-68's unresolved bwrap
`uid map: Permission denied` issue and does not establish that bwrap is fixed.

Reference: https://github.com/paperclipai/paperclip/issues/16337

## Refreshed validation — 2026-10-22 16:20 ART

The prior operator report states that a VPS host-level bwrap check passed with
AppArmor, seccomp, and Codex sandbox enforcement active: Ubuntu `bubblewrap`
was installed, a targeted AppArmor profile was attached to `/usr/bin/bwrap`,
the global `kernel.apparmor_restrict_unprivileged_userns` value remained `1`,
and `codex sandbox /usr/bin/true` exited `0` as `paperclip-runner`. The raw
command output, kernel version, and audit evidence are not attached here, so
this is a recorded claim rather than independently verified host evidence.

Paperclip's existing ORK-40 task also ran public web research and saved a
dated research document plus an internal comment. Its final recovery state
still returned to `Blocked / Agent needs attention` after two automatic
outcome-recovery attempts. That is a separate Paperclip task lifecycle issue;
do not create new copies or retry in a loop. Scheduled routines remain paused
until this post-run state is stable.

The same-day local OSM pilot used the authorized 505-row workbook and canonical
pipeline/control Markdown for partial dedupe in Buenos Aires. OSM returned 4
named records; 0 matched the workbook, 1 matched the history files, and 3 were
exported as Tier C research-only directory records. They lack verified buying
need and full inbox/social/task-history reconciliation. Keep them out of the
contact queue. Output files are in
`/tmp/orkelya-logistics-pilot-2026-10-22-refresh/`; 0 contacts sent and $0
spent.

## Paperclip end-to-end clarification — 2026-10-22 17:28 ART

The 16:20 entry reports a host-level smoke check (`codex sandbox
/usr/bin/true`) as successful, but that check is not proof that Paperclip can
execute and record a work task. The live ORK-68 issue and cancelled ORK-75 test
record Paperclip work failing before command execution with a `bwrap` UID-map
permission error. SSH authentication from the Mac returned
`Permission denied (publickey)`. The host admin still needs to attach the
host/kernel, loaded-profile, and restricted-runner smoke-test evidence; COO must
then verify one harmless Paperclip task end to end. Keep shell-dependent
routines paused until both proofs succeed.

## Local research continuation — 2026-10-22 17:39 ART

Ran the bounded Buenos Aires OSM pilot on the Mac using the authorized 505-row
workbook and canonical pipeline/control Markdown. The export contains three
remaining directory records: Logística Olavarría, SAf Depósito Fiscal, and
Tornus Logistica. All are Tier C, score 0, and explicitly `NOT CONTACTABLE`:
OSM provides directory data, not a current buying signal or buyer identity.
Source edit timestamps are unavailable. Dedupe checked the workbook and the
two Markdown histories, but inboxes, social accounts, and all Paperclip task
history were not verified, so the result remains `PARTIAL` and must not enter
the send queue. No messages were drafted or sent; spend was $0.

The CSV and XLSX were exported to `/tmp/orkelya-run-2026-10-22/`. These local
records provide a research fallback while Paperclip hand-back is broken, but
they do not resolve ORK-23/24 or authorize outreach. Keep commercial routines
paused until an end-to-end Paperclip task finishes and records its outcome,
and keep the Board-only ORK-23 gate with Board.
