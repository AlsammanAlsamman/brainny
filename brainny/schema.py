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

# "skill" vs. "technique": a technique is a described method; a skill is
# a described method with actual evidence attached (see Attachment below)
# — a script, a small illustrative table, a small plot — substantial
# enough to literally follow again, not just read about. Structural
# how-tos ("how this Snakemake project should be laid out", "how the
# GWAS QC step works", "how the manhattan plot is made") are the
# intended shape; use "technique" for anything without real evidence
# attached.
Kind = Literal["technique", "precaution", "solution", "insight", "seed", "skill"]
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
# A small, physical piece of evidence attached to an idea — a script, a
# tiny illustrative table excerpt, a small plot — not the full
# dataset/output, just enough to show the shape/format so a future
# session (human or AI) can follow it without re-deriving it. Stored as
# an actual file under brainny-out/attachments/<idea-id>/ (see
# cli.py's cmd_attach), referenced here by filename only.
AttachmentType = Literal["code", "plot", "table"]

# The cap on Attachment is a file-size cap (cli.py's MAX_ATTACHMENT_BYTES,
# for real files copied to disk). `snippet` is the inline sibling: no file,
# no `brainny attach` call needed — just a piece of text carried straight
# in the entry/node itself for whenever the useful part of an idea already
# *is* text: a code excerpt, a column-by-column table description, an
# equation, a config block, a short schema. Still bounded, same "small
# enough to guide" discipline as attachments -- if it's long enough to need
# trimming down to fit, it probably belongs in a real `code`/`table` file
# via `brainny attach` instead, not squeezed in here.
MAX_SNIPPET_CHARS = 4000


class Attachment(BaseModel):
    type: AttachmentType
    filename: str = Field(min_length=1)
    description: Optional[str] = None


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
    attachments: list[Attachment] = Field(default_factory=list)
    snippet: Optional[str] = Field(default=None, max_length=MAX_SNIPPET_CHARS)

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


# What combining several captured ideas together could become -- SEED.md
# principle #1 ("statistics propose; the AI adjudicates") applies here at
# its purest: this is a pure semantic judgment call (do these ideas
# actually support each other toward something real?), nothing
# deterministic proposes it. `weight` is the AI's own honest confidence
# in the combination, 0.0-1.0 -- same convention as Edge.confidence -- not
# a popularity/vote count, and never fabricated to make an opportunity
# look better. Lives in its own opportunities.json (see opportunities.py),
# sibling to graph.json, same two-contracts discipline (SEED.md §1.6): the
# prompt/skill emits OpportunityInput, the body fills id/created.
OpportunityKind = Literal["tool", "website", "statistical-module", "business-idea", "other"]


class OpportunityInput(BaseModel):
    """What the synthesis skill (skills/brainny/synthesize.md) is allowed
    to fill in. Must NOT set id or created -- the body's job."""

    title: str = Field(min_length=1)
    kind: OpportunityKind
    weight: float = Field(ge=0.0, le=1.0)
    summary: str = Field(min_length=1)
    idea_ids: list[str] = Field(min_length=2)
    rationale: Optional[str] = None


class Opportunity(OpportunityInput):
    id: str
    created: str = Field(default_factory=now_iso)
    session: Optional[str] = None


class Opportunities(BaseModel):
    """opportunities.json — the whole per-project list of proposed
    combinations."""

    items: list[Opportunity] = Field(default_factory=list)
