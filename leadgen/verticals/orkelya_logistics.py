"""Conservative directory discovery for Orkelya logistics systems research.

This vertical finds public OSM directory records only. Sector match is not
buying intent, and every row stays in tier C until separately researched.
"""
from __future__ import annotations

from .. import Vertical, register


def _score(rec: dict) -> tuple[int, str, str]:
    return (
        0,
        "C",
        "OSM directory record only; current need and buyer are unverified; do not contact",
    )


COLUMNS = [
    ("Tier", "tier"),
    ("Score", "score"),
    ("Company", "name"),
    ("Category", "category"),
    ("City", "city"),
    ("Address", "address"),
    ("Public phone", "phone"),
    ("Public email", "email"),
    ("Website", "website"),
    ("Why this is only a candidate", "why"),
    ("Source", "source"),
    ("Source URL", "source_url"),
    ("Observed at UTC", "observed_at_utc"),
    ("Source record updated at", "source_updated_at"),
    ("Research status", "research_status"),
    ("Deduplication status", "dedupe_status"),
]


register(
    Vertical(
        key="orkelya_logistics",
        label="Orkelya logistics directory candidates (research only)",
        description=(
            "Discovers named logistics, transport, and warehouse records from "
            "OpenStreetMap. Every result remains unqualified and non-contactable."
        ),
        osm_tags=[
            "office=logistics",
            "office=transport",
            "industrial=warehouse",
        ],
        keep_chains=True,
        score_fn=_score,
        columns=COLUMNS,
    )
)
