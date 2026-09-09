"""Ingest entries.json → place/grow nodes in graph.json.

v0 scope (see SEED.md §7): no dedup yet (that's dedup.py, v0.1) — every
entry becomes a new node. Placement/growth-vs-spawn arrives with stats.py
and dedup.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from brainny.graph import DEFAULT_OUT_DIR, load_graph, next_id, save_graph
from brainny.schema import EntryInput, GrowthLogEntry, Node, ProvenanceEntry, now_iso


def load_entries(entries_path: Path) -> list[EntryInput]:
    raw = json.loads(Path(entries_path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("entries.json must contain a JSON array of entries")
    return [EntryInput.model_validate(item) for item in raw]


def capture(
    entries_path: Path,
    project: str,
    session: str,
    out_dir: Path = DEFAULT_OUT_DIR,
) -> tuple[list[Node], Path]:
    """Validate entries, spawn a node per entry, write graph.json.

    Returns the newly created nodes and the path written.
    """
    entries = load_entries(entries_path)
    graph = load_graph(out_dir)

    ts = now_iso()
    new_nodes: list[Node] = []
    for entry in entries:
        node = Node(
            **entry.model_dump(),
            id=next_id(graph),
            state="seed",
            provenance=[ProvenanceEntry(project=project, session=session, ts=ts)],
            growth_log=[
                GrowthLogEntry(session=session, ts=ts, event="seeded", note="first captured")
            ],
            recurrence=1,
            last_touched=ts,
        )
        graph.nodes.append(node)
        new_nodes.append(node)

    path = save_graph(graph, out_dir)
    return new_nodes, path
