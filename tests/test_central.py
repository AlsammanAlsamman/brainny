"""brainny/central.py: the merged, read-only cross-project view (OPERATIONS.md
step 19) -- concatenation only, no dedup (that stays v0.4/SEED.md §7).
"""

from pathlib import Path

from brainny.central import build_merged_graph, build_merged_opportunities, list_central_projects
from brainny.graph import save_graph
from brainny.opportunities import save_opportunities
from brainny.schema import Graph, Node, Opportunities, Opportunity, ProvenanceEntry


def _node(id_, project, title="t") -> Node:
    return Node(
        id=id_,
        kind="insight",
        title=title,
        summary="s",
        domain="d",
        provenance=[ProvenanceEntry(project=project, session="s1")],
    )


def test_list_central_projects_empty_when_folder_missing(tmp_path):
    assert list_central_projects(tmp_path / "nope") == []


def test_list_central_projects_ignores_dirs_without_a_graph(tmp_path):
    central = tmp_path / "central"
    (central / "not-a-project").mkdir(parents=True)
    save_graph(Graph(nodes=[_node("idea_0001", "real-project")]), central / "real-project")

    assert list_central_projects(central) == ["real-project"]


def test_build_merged_graph_concatenates_every_project(tmp_path):
    central = tmp_path / "central"
    save_graph(Graph(nodes=[_node("idea_0001", "proj-a", "a1")]), central / "proj-a")
    save_graph(
        Graph(nodes=[_node("idea_0001", "proj-b", "b1"), _node("idea_0002", "proj-b", "b2")]),
        central / "proj-b",
    )

    merged = build_merged_graph(central)
    assert len(merged.nodes) == 3
    titles = sorted(n.title for n in merged.nodes)
    assert titles == ["a1", "b1", "b2"]


def test_build_merged_graph_keeps_original_ids_even_when_they_collide(tmp_path):
    # each project numbers its own ideas independently -- "idea_0001" in
    # proj-a and "idea_0001" in proj-b are different ideas; the merge must
    # not silently rewrite/lose one of them
    central = tmp_path / "central"
    save_graph(Graph(nodes=[_node("idea_0001", "proj-a")]), central / "proj-a")
    save_graph(Graph(nodes=[_node("idea_0001", "proj-b")]), central / "proj-b")

    merged = build_merged_graph(central)
    ids = [n.id for n in merged.nodes]
    assert ids == ["idea_0001", "idea_0001"]
    projects = [n.provenance[0].project for n in merged.nodes]
    assert sorted(projects) == ["proj-a", "proj-b"]


def test_build_merged_graph_empty_when_no_projects(tmp_path):
    central = tmp_path / "central"
    central.mkdir()
    merged = build_merged_graph(central)
    assert merged.nodes == []


def _opp(id_, idea_ids, title="t") -> Opportunity:
    return Opportunity(id=id_, title=title, kind="tool", weight=0.5, summary="s", idea_ids=idea_ids)


def test_build_merged_opportunities_namespaces_idea_ids_by_project(tmp_path):
    central = tmp_path / "central"
    save_graph(Graph(nodes=[_node("idea_0001", "proj-a")]), central / "proj-a")
    save_opportunities(
        Opportunities(items=[_opp("opp_0001", ["idea_0001", "idea_0002"])]), central / "proj-a"
    )

    merged = build_merged_opportunities(central)
    assert len(merged.items) == 1
    assert merged.items[0].idea_ids == ["proj-a::idea_0001", "proj-a::idea_0002"]


def test_build_merged_opportunities_concatenates_across_projects(tmp_path):
    # list_central_projects() (and so build_merged_opportunities) only
    # recognizes a folder as a synced project once it has a graph.json --
    # realistic, since `brainny propose` always requires one to validate
    # idea_ids against in the first place.
    central = tmp_path / "central"
    save_graph(Graph(nodes=[_node("idea_0001", "proj-a")]), central / "proj-a")
    save_graph(Graph(nodes=[_node("idea_0001", "proj-b")]), central / "proj-b")
    save_opportunities(Opportunities(items=[_opp("opp_0001", ["a", "b"], "t1")]), central / "proj-a")
    save_opportunities(Opportunities(items=[_opp("opp_0001", ["c", "d"], "t2")]), central / "proj-b")

    merged = build_merged_opportunities(central)
    titles = sorted(o.title for o in merged.items)
    assert titles == ["t1", "t2"]


def test_build_merged_opportunities_empty_when_none_proposed(tmp_path):
    central = tmp_path / "central"
    save_graph(Graph(nodes=[_node("idea_0001", "proj-a")]), central / "proj-a")

    merged = build_merged_opportunities(central)
    assert merged.items == []
