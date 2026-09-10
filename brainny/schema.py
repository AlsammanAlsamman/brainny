"""The entry/node schema — §4 of SEED.md, the single source of truth.

One shape serves two purposes:
- EntryInput: what the capture prompt (Part 1) emits — a bare JSON entry.
- Node: what lives in graph.json (Part 3) — an EntryInput plus everything
  the body (Part 2) fills in during capture/dedup/decay.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Kind = Literal["technique", "precaution", "solution", "insight", "seed"]
State = Literal["seed", "sprouting", "mature", "harvested"]
# Who actually originated the idea's content — not who ran the capture
# command. "human": the person explicitly pointed at it (e.g.
# /brainny-catch-this is always this, by construction — the user just
# described it). "ai": the assistant noticed/figured it out itself
# (a mistake it caught, a technique it landed on) without the human
# calling it out. "collaborative": genuinely built together, back and
# forth. Optional/None on older entries captured before this field
# existed — "unclassified", not a fourth category.
Origin = Literal["human", "ai", "collaborative"]
EdgeType = Literal[
    "derived-from", "refines", "contradicts", "combines-with", "same-technique"
]
EdgeSource = Literal["extracted", "inferred"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ProvenanceEntry(BaseModel):
    project: str
    session: str
    ts: str = Field(default_factory=now_iso)


class GrowthLogEntry(BaseModel):
    session: str
    ts: str = Field(default_factory=now_iso)
    event: str
    note: Optional[str] = None


class Edge(BaseModel):
    target: str
    type: EdgeType
    confidence: float = Field(ge=0.0, le=1.0)
    source: EdgeSource = "inferred"


class EntryInput(BaseModel):
    """What the capture prompt (Part 1 — SKILL.md) is allowed to fill in.

    The prompt must NOT set id, embedding, edges, novelty, recurrence,
    state, or provenance timestamps — those are the body's job.
    """

    kind: Kind
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    detail: Optional[str] = None
    domain: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    trigger: Optional[str] = None
    origin: Optional[Origin] = None

    @field_validator("trigger")
    @classmethod
    def trigger_only_for_precautions(cls, v, info):
        # trigger is meaningful only for precautions; harmless if set elsewhere,
        # so we don't hard-reject, just leave it — the body ignores it otherwise.
        return v


class Node(EntryInput):
    """The full graph node — an EntryInput plus body-filled fields."""

    id: str
    state: State = "seed"
    provenance: list[ProvenanceEntry] = Field(default_factory=list)
    growth_log: list[GrowthLogEntry] = Field(default_factory=list)
    edges: list[Edge] = Field(default_factory=list)
    embedding: list[float] = Field(default_factory=list)
    novelty: Optional[float] = None
    recurrence: int = 1
    last_touched: str = Field(default_factory=now_iso)


class Graph(BaseModel):
    """graph.json — the whole per-project brain."""

    nodes: list[Node] = Field(default_factory=list)
