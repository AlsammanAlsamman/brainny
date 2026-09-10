"""render_html / save_html: the v0.2 dashboard visualization — a D3
dropdown (radial tree / force network) plus an itemized accordion list,
folded in from examples/ once that exploration settled (see the
conversation, and OPERATIONS.md's viz history).

The page is mostly JS-driven, so these tests check the things that are
actually ours to get right: the payload is correct, untrusted content
can't break out of the embedded <script type="application/json"> block,
and the page structure the JS depends on (dropdown, mount points) exists.
"""

import json
import re
from pathlib import Path

from brainny.capture import capture
from brainny.graph import load_graph
from brainny.schema import Graph, Node
from brainny.viz import render_html, save_html

FIXTURES = Path(__file__).parent / "fixtures"


def _extract_payload(html: str) -> dict:
    m = re.search(
        r'<script id="brainny-data" type="application/json">(.*?)</script>', html, re.S
    )
    assert m, "brainny-data payload script not found"
    return json.loads(m.group(1))


def test_render_html_empty_graph():
    out = render_html(Graph())
    assert out.strip().startswith("<!doctype html>")
    payload = _extract_payload(out)
    assert payload["nodes"] == []
    assert payload["sessions"] == []
    assert "No ideas captured yet" in out


def test_render_html_payload_matches_graph(tmp_path):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)
    graph = load_graph(out_dir)

    out = render_html(graph)
    payload = _extract_payload(out)

    assert len(payload["nodes"]) == 2
    titles = {n["title"] for n in payload["nodes"]}
    assert "Two-pass capture: project-aware then project-blind" in titles
    assert payload["sessions"] == [{"session": "s1", "ts": payload["sessions"][0]["ts"], "count": 2}]
    assert payload["domainCount"] == 1


def test_render_html_payload_groups_multiple_sessions(tmp_path):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)
    capture(FIXTURES / "sample_entries.json", project="p", session="s2", out_dir=out_dir)
    graph = load_graph(out_dir)

    payload = _extract_payload(render_html(graph))
    sessions = {s["session"]: s["count"] for s in payload["sessions"]}
    assert sessions == {"s1": 2, "s2": 2}


def test_render_html_escapes_script_breakout():
    graph = Graph(
        nodes=[
            Node(
                kind="insight",
                title="</script><script>alert(1)</script>",
                summary="ok & safe",
                domain="d",
                id="idea_0001",
            )
        ]
    )
    out = render_html(graph)
    payload = _extract_payload(out)
    assert payload["nodes"][0]["title"] == "</script><script>alert(1)</script>"
    # the raw closing sequence must not appear unescaped inside the data block
    assert "<\\/script>" in out


def test_render_html_embeds_d3_with_no_cdn_dependency():
    # D3 is vendored and baked directly into the HTML (brainny/viz.py's
    # _D3_JS) so the dashboard renders with zero network access -- a real
    # user's central-folder graph.html rendered blank because the old CDN
    # <script src> silently failed to load offline. No cdn.jsdelivr.net
    # reference should remain, and the actual library source must be here.
    out = render_html(Graph())
    assert "cdn.jsdelivr.net" not in out
    assert "<script src=" not in out
    assert "d3js.org v7.9.0" in out  # D3's own version banner comment
    # no leftover references to the retired 3D-tree-browser implementation
    assert "three@" not in out
    assert "3d-force-graph" not in out
    assert "ForceGraph3D" not in out


def test_render_html_has_dropdown_and_mount_points():
    out = render_html(Graph())
    assert '<select id="view-select">' in out
    assert 'value="radial"' in out
    assert 'value="force"' in out
    assert 'id="item-list-mount"' in out
    assert 'id="viz"' in out
    assert 'id="tooltip"' in out


def test_render_html_domain_split_for_sub_branches():
    graph = Graph(
        nodes=[
            Node(kind="technique", title="t1", summary="s1", domain="GWAS / merging", id="idea_0001"),
            Node(kind="insight", title="t2", summary="s2", domain="GWAS", id="idea_0002"),
        ]
    )
    payload = _extract_payload(render_html(graph))
    domains = {n["id"]: n["domain"] for n in payload["nodes"]}
    assert domains == {"idea_0001": "GWAS / merging", "idea_0002": "GWAS"}
    assert payload["domainCount"] == 2


def test_save_html_writes_file(tmp_path):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)
    graph = load_graph(out_dir)

    path = save_html(graph, out_dir)
    assert path == out_dir / "graph.html"
    assert path.exists()
    payload = _extract_payload(path.read_text(encoding="utf-8"))
    assert len(payload["nodes"]) == 2
