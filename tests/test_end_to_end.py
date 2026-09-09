"""Layer 6 (SEED.md §6) smoke test, v0 slice: capture -> graph.json grows -> query returns it.

grow/neglected/serve pieces of this layer land with stats.py, dedup.py and
serve.py in later roadmap stages — not part of the v0 slice.
"""

from pathlib import Path

from brainny.capture import capture
from brainny.graph import load_graph
from brainny.viz import render_tree

FIXTURES = Path(__file__).parent / "fixtures"


def test_capture_then_query_smoke(tmp_path):
    out_dir = tmp_path / "out"

    capture(FIXTURES / "sample_entries.json", project="brainny", session="design-s1", out_dir=out_dir)

    graph = load_graph(out_dir)
    tree = render_tree(graph)

    assert "2 idea(s)" in tree
    assert "Two-pass capture" in tree
    assert "Never let a similarity threshold" in tree
    assert "brainny-design/" in tree


def test_render_tree_empty_graph():
    from brainny.schema import Graph

    tree = render_tree(Graph())
    assert "no ideas captured yet" in tree
