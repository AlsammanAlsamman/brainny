"""brainny/badge.py: the small, optional SVG activity badge for a GitHub
profile README -- counts/shape only, never idea content (OPERATIONS.md
step 22).
"""

from datetime import datetime, timedelta, timezone

from brainny.badge import compute_badge_stats, render_badge_svg
from brainny.schema import Graph, Node, ProvenanceEntry


def _node(id_, kind, project="p", domain="d", days_ago=0, title="a secret title") -> Node:
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(timespec="seconds")
    return Node(
        id=id_, kind=kind, title=title, summary="s", domain=domain,
        provenance=[ProvenanceEntry(project=project, session="s1")],
        last_touched=ts,
    )


def test_compute_badge_stats_counts_by_kind_and_domain():
    graph = Graph(nodes=[
        _node("idea_0001", "skill", project="a", domain="d1"),
        _node("idea_0002", "precaution", project="a", domain="d1"),
        _node("idea_0003", "technique", project="b", domain="d2"),
    ])
    stats = compute_badge_stats(graph)
    assert stats["total"] == 3
    assert stats["by_kind"]["skill"] == 1
    assert stats["by_kind"]["precaution"] == 1
    assert stats["domains"] == 2
    assert stats["projects"] == 2


def test_compute_badge_stats_recent_window_is_three_days():
    graph = Graph(nodes=[
        _node("idea_0001", "insight", days_ago=1),
        _node("idea_0002", "insight", days_ago=10),
    ])
    stats = compute_badge_stats(graph)
    assert stats["recent"] == 1


def test_compute_badge_stats_empty_graph():
    stats = compute_badge_stats(Graph())
    assert stats["total"] == 0
    assert stats["domains"] == 0
    assert stats["projects"] == 0
    assert stats["recent"] == 0


def test_render_badge_svg_is_valid_svg_shape():
    graph = Graph(nodes=[_node("idea_0001", "skill")])
    svg = render_badge_svg(graph)
    assert svg.strip().startswith("<svg")
    assert svg.strip().endswith("</svg>")
    assert "viewBox" in svg


def test_render_badge_svg_never_leaks_idea_content():
    # a profile README is public; the graph's own titles/summaries are not
    # meant to be -- the badge must only ever show counts/shape
    graph = Graph(nodes=[_node("idea_0001", "precaution", title="A VERY SECRET TITLE")])
    svg = render_badge_svg(graph)
    assert "A VERY SECRET TITLE" not in svg


def test_render_badge_svg_escapes_title():
    svg = render_badge_svg(Graph(), title="<script>alert(1)</script>")
    assert "<script>alert(1)</script>" not in svg
    assert "&lt;script&gt;" in svg
