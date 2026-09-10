"""Read/write opportunities.json -- mirrors test_graph.py's shape for
graph.json (there is no test_graph.py; graph.py's load/save is covered
indirectly through capture/cli tests, so this file covers opportunities.py
directly since nothing else does).
"""

from pathlib import Path

from brainny.opportunities import (
    load_opportunities,
    next_opportunity_id,
    opportunities_path,
    save_opportunities,
)
from brainny.schema import Opportunities, Opportunity


def _opp(id_, title="t") -> Opportunity:
    return Opportunity(id=id_, title=title, kind="tool", weight=0.5, summary="s", idea_ids=["a", "b"])


def test_load_opportunities_returns_empty_when_file_missing(tmp_path):
    result = load_opportunities(tmp_path)
    assert result.items == []


def test_save_and_load_opportunities_roundtrip(tmp_path):
    opportunities = Opportunities(items=[_opp("opp_0001"), _opp("opp_0002", "t2")])
    save_opportunities(opportunities, tmp_path)

    assert opportunities_path(tmp_path).exists()
    loaded = load_opportunities(tmp_path)
    assert len(loaded.items) == 2
    assert loaded.items[0].id == "opp_0001"


def test_next_opportunity_id_starts_at_0001():
    assert next_opportunity_id(Opportunities()) == "opp_0001"


def test_next_opportunity_id_increments_and_avoids_collision():
    opportunities = Opportunities(items=[_opp("opp_0001"), _opp("opp_0002")])
    assert next_opportunity_id(opportunities) == "opp_0003"
