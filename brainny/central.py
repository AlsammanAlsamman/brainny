"""The central tier (SEED.md §2/§1.7): a read-only MERGE across every
project synced into the configured central folder.

This is deliberately NOT the full v0.4 "mature" central.py from SEED.md's
roadmap (§7) -- that one reconciles: dedup, cross-project connections, a
single canonical ~/.brainny/global.json other tools write into. Building
that half-right would be worse than not building it (SEED.md's own "stats
propose, AI adjudicates" principle means dedup needs a real semantic
judgment call, not a naive id/title match). What's here is the honest
subset that's actually useful today: literally concatenate every synced
project's nodes into one Graph so there's a single place to *look*, with
no pretense of reconciliation. `brainny central --html` is the command
that uses this.
"""

from __future__ import annotations

from pathlib import Path

from brainny.graph import graph_path, load_graph
from brainny.opportunities import load_opportunities
from brainny.schema import Graph, Node, Opportunities


def list_central_projects(central_root: Path) -> list[str]:
    """Every immediate subfolder of the central folder that's actually a
    synced project (has its own graph.json) -- not just any directory that
    happens to live there."""
    if not central_root.is_dir():
        return []
    return sorted(p.name for p in central_root.iterdir() if p.is_dir() and graph_path(p).exists())


def build_merged_graph(central_root: Path) -> Graph:
    """Concatenate every synced project's nodes into one Graph, untouched --
    node ids stay exactly what's on disk in that project's own graph.json
    (they're only unique WITHIN a project's own file: each project numbers
    its own ideas idea_0001, idea_0002, ... independently, so two different
    projects can and often will share an id). Deliberately NOT namespaced
    here: attachments are referenced by that real id + the project's own
    folder name (viz.py's dashboard resolves the path as
    "<project>/attachments/<id>/<filename>" for a merged view), so mangling
    the id at merge time would break that. Where the dashboard needs a
    globally-unique key for DOM/d3 purposes (two projects both having an
    "idea_0001"), it derives one client-side from `project` + `id` together
    -- see viz.py's `itemKey()` -- rather than this module rewriting
    identity that belongs to each project."""
    nodes: list[Node] = []
    for project in list_central_projects(central_root):
        nodes.extend(load_graph(central_root / project).nodes)
    return Graph(nodes=nodes)


def build_merged_opportunities(central_root: Path) -> Opportunities:
    """Concatenate every synced project's proposed opportunities into one
    Opportunities. Unlike build_merged_graph(), idea_ids here ARE
    rewritten to "<project>::<id>" -- an opportunity only makes sense
    alongside the ideas it references, and in the merged dashboard those
    ideas are addressed by the same project-qualified key viz.py's
    itemKey() computes (since raw ids collide across projects). This
    keeps an opportunity's "built from" links resolvable in the merged
    view without viz.py needing to know anything about central.py."""
    items = []
    for project in list_central_projects(central_root):
        for opp in load_opportunities(central_root / project).items:
            items.append(
                opp.model_copy(update={"idea_ids": [f"{project}::{iid}" for iid in opp.idea_ids]})
            )
    return Opportunities(items=items)
