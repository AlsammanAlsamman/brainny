"""Layer 4 (SEED.md §6): capture contract at the body level.

The prompt's job (gate, two passes) is out of scope here — this tests that
`brainny.capture` turns a valid entries.json into graph nodes correctly,
and that an empty array is a valid, correct outcome.
"""

import json
from pathlib import Path

from brainny.capture import capture
from brainny.graph import load_graph

FIXTURES = Path(__file__).parent / "fixtures"


def test_capture_empty_array_yields_no_nodes(tmp_path):
    entries_path = tmp_path / "entries.json"
    entries_path.write_text("[]", encoding="utf-8")

    nodes, graph_file = capture(entries_path, project="p", session="s1", out_dir=tmp_path / "out")

    assert nodes == []
    assert graph_file.exists()
    graph = load_graph(tmp_path / "out")
    assert graph.nodes == []


def test_capture_sample_entries(tmp_path):
    out_dir = tmp_path / "out"
    nodes, graph_file = capture(
        FIXTURES / "sample_entries.json", project="brainny", session="design-s1", out_dir=out_dir
    )

    assert len(nodes) == 2
    assert nodes[0].id == "idea_0001"
    assert nodes[1].id == "idea_0002"
    assert nodes[0].kind == "technique"
    assert nodes[1].kind == "precaution"
    assert nodes[0].state == "seed"
    assert nodes[0].provenance[0].project == "brainny"
    assert nodes[0].provenance[0].session == "design-s1"
    assert nodes[0].growth_log[0].event == "seeded"

    graph = load_graph(out_dir)
    assert len(graph.nodes) == 2

    data = json.loads(graph_file.read_text(encoding="utf-8"))
    assert len(data["nodes"]) == 2


def test_capture_appends_to_existing_graph(tmp_path):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)
    nodes2, _ = capture(FIXTURES / "sample_entries.json", project="p", session="s2", out_dir=out_dir)

    assert nodes2[0].id == "idea_0003"
    graph = load_graph(out_dir)
    assert len(graph.nodes) == 4
