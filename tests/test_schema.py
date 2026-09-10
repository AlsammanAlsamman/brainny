"""Layer 1 (SEED.md §6): schema is pure and strict.

Valid entries parse; malformed ones are rejected; body-filled fields
default correctly.
"""

import pytest
from pydantic import ValidationError

from brainny.schema import EntryInput, Node


def test_valid_entry_parses():
    entry = EntryInput(
        kind="precaution",
        title="Verify no duplicate/overlapping inputs before merging datasets",
        summary="Before combining sources, check for overlap; duplicates silently skew the result.",
        domain="data-eng",
        tags=["data-quality", "merge"],
        trigger="before merging or combining multiple data sources",
    )
    assert entry.kind == "precaution"
    assert entry.trigger is not None


def test_entry_minimal_fields():
    entry = EntryInput(kind="insight", title="t", summary="s", domain="d")
    assert entry.detail is None
    assert entry.tags == []
    assert entry.trigger is None
    assert entry.origin is None  # unclassified, not a guessed default


@pytest.mark.parametrize("origin", ["human", "ai", "collaborative"])
def test_entry_accepts_each_origin(origin):
    entry = EntryInput(kind="insight", title="t", summary="s", domain="d", origin=origin)
    assert entry.origin == origin


def test_entry_rejects_invalid_origin():
    with pytest.raises(ValidationError):
        EntryInput(kind="insight", title="t", summary="s", domain="d", origin="robot")


@pytest.mark.parametrize(
    "bad_kwargs",
    [
        {"kind": "not-a-kind", "title": "t", "summary": "s", "domain": "d"},
        {"kind": "seed", "title": "", "summary": "s", "domain": "d"},
        {"kind": "seed", "title": "t", "summary": "", "domain": "d"},
        {"kind": "seed", "title": "t", "summary": "s", "domain": ""},
        {"title": "t", "summary": "s", "domain": "d"},  # missing kind
    ],
)
def test_malformed_entries_rejected(bad_kwargs):
    with pytest.raises(ValidationError):
        EntryInput(**bad_kwargs)


def test_node_defaults_body_filled_fields():
    node = Node(
        kind="technique",
        title="t",
        summary="s",
        domain="d",
        id="idea_0001",
    )
    assert node.state == "seed"
    assert node.provenance == []
    assert node.growth_log == []
    assert node.edges == []
    assert node.embedding == []
    assert node.novelty is None
    assert node.recurrence == 1
    assert node.last_touched  # auto-populated timestamp


def test_node_requires_id():
    with pytest.raises(ValidationError):
        Node(kind="technique", title="t", summary="s", domain="d")


def test_edge_confidence_bounds():
    from brainny.schema import Edge

    Edge(target="idea_0001", type="refines", confidence=0.0)
    Edge(target="idea_0001", type="refines", confidence=1.0)
    with pytest.raises(ValidationError):
        Edge(target="idea_0001", type="refines", confidence=1.5)
