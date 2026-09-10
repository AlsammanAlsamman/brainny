"""Read/write opportunities.json -- the per-project list of AI-proposed
combinations (SEED.md principle #1: "statistics propose; the AI
adjudicates"), sibling to graph.json. Mirrors graph.py's shape exactly on
purpose, same load/save/next_id discipline, so cli.py's central-mirror
and central.py's merge logic can treat both the same way.
"""

from __future__ import annotations

import json
from pathlib import Path

from brainny.graph import DEFAULT_OUT_DIR
from brainny.schema import Opportunities

OPPORTUNITIES_FILENAME = "opportunities.json"


def opportunities_path(out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    return out_dir / OPPORTUNITIES_FILENAME


def load_opportunities(out_dir: Path = DEFAULT_OUT_DIR) -> Opportunities:
    path = opportunities_path(out_dir)
    if not path.exists():
        return Opportunities()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Opportunities.model_validate(data)


def save_opportunities(opportunities: Opportunities, out_dir: Path = DEFAULT_OUT_DIR) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = opportunities_path(out_dir)
    path.write_text(
        json.dumps(opportunities.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def next_opportunity_id(opportunities: Opportunities) -> str:
    n = len(opportunities.items) + 1
    while True:
        candidate = f"opp_{n:04d}"
        if not any(item.id == candidate for item in opportunities.items):
            return candidate
        n += 1
