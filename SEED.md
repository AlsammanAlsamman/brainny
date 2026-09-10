# brAInny — SEED

> The living seed document. Everything the project needs to start, test, and grow lives here until the codebase outgrows it. When a section here becomes real code with its own tests, thin it down to a pointer. The doc shrinks as the project grows — that's the sign it's working.

---

## 0. What brАInny is (the north star)

**brAInny remembers *how you work* — the techniques you invent and the precautions you learn while solving problems with AI — so you stop re-learning your own lessons.**

Not a note app. Not "capture your ideas." The real target is the **procedural residue** of working with AI: the methods, gotchas, and solutions that get generated *in passing* while you solve something else, and evaporate when the session ends because they weren't the point of the session.

**For anyone who works with AI — not any one field.** A developer's keeper is a code pattern or a gotcha; a designer's is a layout system or a color rule; a lawyer's is a clause or an argument structure; a writer's is a voice or an outline that worked; a marketer's is a positioning angle; a researcher's is a method or a precaution. brAInny privileges none of them — it *learns* what "reusable" means per project (see the project-nature descriptor and the project-blind pass in §1). The domain is whatever the user is working in.

Examples that must never be lost again (across domains):
- Took a **precaution once** — a check, a validation step, a "don't forget to…" — never wrote it down, forgot it next time.
- Found a **structure you like and maintain well** (a project layout, a document skeleton, a workflow) and lost it.
- Solved a fiddly problem with a **specific working approach** you'll hit again but won't remember how you cracked.

Canonical name: `brainny` (lowercase, one word, double-N) everywhere a machine reads it — CLI, package, repo, `brainny-out/`. Stylized **brAInny** only on human surfaces (logo, site, README headline).

Modeled on graphify's delivery model: a **local skill + CLI** that emits **git-shareable output**, with a **per-project graph + a central cross-project graph**. Nothing runs on a server.

---

## 1. Core principles (the constitution — don't violate these)

1. **Statistics propose; the AI adjudicates.** The deterministic layer scores and shortlists (cheap, local). The model makes the semantic calls (worth keeping? same idea or just adjacent? what kind of edge?). Never let a similarity threshold auto-decide keep/drop.
2. **Ideas are nodes; sessions are provenance.** A session is an *event* where ideas appear or grow. Most captures **attach as a growth event** to an existing idea; only sometimes spawn a new node.
3. **Projects capture; central reconciles.** Dedup and cross-project connection-finding live in the central tier, the only layer that sees everything.
4. **Two-pass capture.** A project-aware pass (high precision, tuned to the domain) *and* a deliberately project-blind pass (high recall, flags the off-topic "unseen giant" as an unplaced `seed`). Precision and recall conflict, so use two passes, not one filter.
5. **Time is the arbiter.** Don't judge a stray thought at capture — capture it cheaply as a `seed` and let **recurrence promote it** or **decay fade it**.
6. **Two contracts, nothing else crosses layers.** Prompt → Body is a **JSON entry**. Body → AI/Viz is **`graph.json` + MCP tools**. Everything else is internal to one part. This is what keeps it simple and portable across Claude CLI and any other assistant.
7. **Asymmetric sync.** Project → central: always. Central → project: only on explicit request, never auto-committed (a shared team repo must never receive private central ideas).
8. **Higher bar than "is this useful?"** Capture a technique only when it's **reusable beyond this task** *and* **non-obvious enough not to want to re-derive.** "I used a for-loop" → no. "The METAL duplication precaution and why it bites" → yes.

---

## 2. The three parts

```
[ Assistant session ]
        │  Part 1: SKILL.md prompt → emits JSON entry
        ▼
   brainny capture           ← Part 2: Python body (stats, dedup, decay, placement)
        │  hands shortlist UP for the semantic call, gets verdict, writes files
        ▼
  brainny-out/graph.json  +  ~/.brainny/global.json
        │  Part 3: the output contract, read three ways
        ├── graph.html         (visualization)
        ├── graph.json         (extensible open format)
        └── brainny serve →MCP (AI-accessible: query + proactive surfacing)
```

- **Part 1 — Prompts (thin, AI-facing).** A `SKILL.md` + templates. Markdown, not code. Emits one JSON entry per keeper. Does *not* dedup/connect/place. Portable: any assistant that reads an instruction file and runs a shell command can drive brainny.
- **Part 2 — Body (thick, AI-agnostic Python).** The `brainny` CLI. Does the deterministic work. When a semantic judgment is needed, hands the shortlist *up* to the assistant already in the session rather than calling an API itself.
- **Part 3 — Output contract.** `graph.html` (viz), `graph.json` (extensible), MCP server (AI-accessible + proactive precaution surfacing).

---

## 3. THING #1 — The starting prompt

This is the seed of `skills/brainny/SKILL.md`. It is what the assistant reads. Start by pasting it manually at the end of a session; formalize into an installed skill later.

````markdown
# brainny — capture skill

You help the user keep a durable memory of the *reusable* things produced while
working with AI — techniques, precautions, solutions, insights — plus stray
ideas that could grow into something later. You run at the END of a working
session, or when the user types `/brainny`.

## What you are looking at
The current session is already in your context. You do not fetch anything.
You also have (or ask for) a one-line PROJECT NATURE descriptor that says what
this project IS and what counts as reusable HERE. It differs entirely by field —
for example:
- "web app / TypeScript + React; reusable = code patterns, gotchas, config"
- "brand design; reusable = layout systems, type/color rules, critique heuristics"
- "contract review; reusable = clauses, argument structures, red-flag checks"
- "long-form writing; reusable = outlines that worked, voice notes, structure"
If none exists, infer a short one from the session and note it.

## Run TWO passes

### Pass 1 — project-aware harvest (precision)
Given the project's nature, find the things that are reusable *in this kind of
work*. For each, decide its `kind`:
- `technique` — a reusable method / how-I-did-X
- `precaution` — a gotcha / check that was (or should have been) done; NEGATIVE
  knowledge, the highest-value and most-forgotten class
- `solution` — a concrete working answer to a specific problem, worth reusing
- `insight` — a conceptual realization

### Pass 2 — project-blind seed catcher (recall)
Ignore the project's nature entirely. Look for the tangent — the "huh, that's
interesting and unrelated" moment, the off-topic spark. Do NOT classify or place
it. Emit it as `kind: seed`. Bias toward flagging; time will sort it out.

## The GATE (apply hard)
For Pass 1, the default answer is usually NO. Emit an entry ONLY if it is:
- reusable BEYOND this one task, AND
- non-obvious enough that re-deriving it would cost real effort.
Most sessions yield 0–2 entries. Emitting nothing is a correct, common outcome.

## What you MUST NOT do
Do not dedup. Do not decide which existing idea this connects to. Do not invent
edges. Placement, dedup, and connection are the body's job — you only describe
what THIS session produced.

## Output
Emit a JSON array of entries matching the schema in §4 (may be empty `[]`),
then shell out:
```
brainny capture <path-to-entries.json>
```
For each entry fill: kind, title, summary (in the user's own reusable terms),
detail (optional), domain/tags, and — for precautions — a `trigger` describing
WHEN brainny should proactively surface it ("starting a METAL/GWAS run").
Leave id, embedding, edges, novelty, recurrence, state, and provenance
timestamps EMPTY — the body fills those.
````

A second template, `prompts/project-nature.md`, produces/refreshes the one-line project descriptor Pass 1 reads.

---

## 4. The entry schema (the keystone)

This one shape is **both** the JSON entry (Part 1 → Body) **and** the node format inside `graph.json` (Part 3). Fields the prompt fills vs. the body fills are marked.

```jsonc
{
  // ---- filled by the PROMPT (Part 1) ----
  "kind": "precaution",           // technique | precaution | solution | insight | seed
  "title": "Verify no duplicate/overlapping inputs before merging datasets",
  "summary": "Before combining sources, check for overlap; duplicates silently skew the result.",
  "detail": "…optional longer note, in the user's reusable terms…",
  "domain": "<whatever the project is>",
  "tags": ["data-quality", "merge", "validation"],
  "trigger": "before merging or combining multiple data sources",  // precautions only: when to surface
  "origin": "human",             // human | ai | collaborative | null (unclassified) — who actually
                                  // originated the idea's content, not who ran the capture command

  // ---- filled by the BODY (Part 2) ----
  "id": "idea_0007",
  "state": "seed",               // growth axis: seed → sprouting → mature → harvested
  "provenance": [
    { "project": "gwas-2026", "session": "s3", "ts": "2026-09-08T12:00:00Z" }
  ],
  "growth_log": [                // the temporal tree — how it matured
    { "session": "s3",  "ts": "…", "event": "seeded",   "note": "first captured" },
    { "session": "s7",  "ts": "…", "event": "advanced", "note": "reused, added edge case" }
  ],
  "edges": [                     // typed + confidence, graphify-style
    { "target": "idea_0002", "type": "refines", "confidence": 0.8, "source": "inferred" }
    // edge types: derived-from | refines | contradicts | combines-with | same-technique
    // source: extracted | inferred
  ],
  "embedding": [/* local sentence-transformer vector */],
  "novelty": 0.42,               // distance to nearest existing idea (a BAND, not higher=better)
  "recurrence": 3,               // how many sessions/projects this theme has surfaced in
  "last_touched": "2026-09-08T12:00:00Z"  // drives decay / neglect nudges
}
```

Why each field earns its place: `embedding`+`novelty` → candidate neighbors & the novelty band; `provenance`+`recurrence` → recurrence signal & seed promotion; `growth_log`+`state` → the temporal tree; `edges` → the typed graph; `last_touched` → decay math; `trigger` → proactive surfacing; `origin` → who to credit — the human supplies direction and innovation, the AI supplies collective/pattern knowledge, and a lot of real work is genuinely both; keeping that distinction visible (and filterable — see the dashboard's origin filter) is what keeps brainny from flattening into an undifferentiated pile of "stuff that happened."

---

## 5. THING #2 — Project structure

Mirrors graphify so the shape is familiar and the plumbing is proven.

```
brainny/
├── brainny/                    # Part 2 — the body (AI-agnostic Python package)
│   ├── __init__.py
│   ├── cli.py                  # entry: capture | query | grow | neglected | install | serve | hook
│   ├── schema.py               # §4 as pydantic models — the single source of truth
│   ├── capture.py              # ingest entries.json → place/grow nodes
│   ├── stats.py                # embeddings, candidate neighbors, novelty band, recurrence, decay
│   ├── dedup.py                # central match: grow existing vs. spawn new
│   ├── graph.py                # node/edge model, read/write graph.json
│   ├── central.py              # ~/.brainny/global.json, asymmetric sync
│   ├── viz.py                  # graph.html (terminal tree first, HTML later)
│   └── serve.py                # Part 3 — MCP server (query_brain, surface_precautions, …)
│
├── skills/brainny/SKILL.md     # Part 1 — the capture prompt (§3)
├── prompts/
│   ├── capture.md              # capture prompt template
│   └── project-nature.md       # project-nature profiler
│
├── tests/                      # Part 3 of THIS doc — see §6
│   ├── fixtures/               # sample sessions + golden expected entries
│   ├── test_schema.py
│   ├── test_stats.py
│   ├── test_dedup.py
│   ├── test_capture.py
│   ├── test_giant.py           # the "does it catch the off-topic seed?" eval
│   └── test_end_to_end.py
│
├── brainny-out/                # per-project output (committed to git)
│   ├── graph.json              # the brain (open format)
│   ├── graph.html              # the visualization
│   └── sessions/               # raw logs as provenance — OUTSIDE the graph
│
├── pyproject.toml              # package = "brainny" (confirmed free on PyPI 2026-09-09)
├── LICENSE                     # MIT
├── README.md
└── SEED.md                     # this file
```

Central brain lives outside any project: `~/.brainny/global.json`.

---

## 6. THING #3 — How to test it

The trick to testing an LLM-in-the-loop system: **test the deterministic parts hard, and pin the fuzzy parts with fixtures + a rubric.** Everything the body does is a pure function with known inputs — test those relentlessly. The AI's judgment is fuzzy — test it against golden examples and accept a pass band.

**Layer 1 — Schema (pure, strict).** Valid entries parse; malformed ones are rejected; body-filled fields default correctly. Fast, deterministic.

**Layer 2 — Stats (pure, seedable).** With a fixed set of entries and a seeded embedding, assert: neighbor ranking is stable, the novelty band classifies a near-duplicate as "too close" and an unrelated note as "too far," recurrence counting is exact, decay arithmetic matches expected timestamps. No AI involved.

**Layer 3 — Dedup (golden fixtures).** "Revenue forecast" vs. "predicting next quarter's income" → MATCH (grow existing). Two genuinely distinct ideas → no match. This is where local embeddings must beat word-matching; the fixture proves it.

**Layer 4 — Capture contract.** Feed a recorded session + a mocked/real prompt output; assert the emitted JSON parses as valid schema and the gate behaved (a trivial "I used a for-loop" session yields `[]`).

**Layer 5 — The giant test (`test_giant.py`).** Feed a session whose main task is mundane but which contains ONE buried off-topic gem. Assert a `kind: seed` node is created. This is the recall guarantee — the whole reason Pass 2 exists. If this test rots, brainny silently starts losing giants.

**Layer 6 — End-to-end smoke.** capture → `graph.json` grows → `query` returns it → after simulated time, `neglected` surfaces it → a precaution's `trigger` fires via `surface_precautions`.

**Layer 7 — Dogfood + honest review (graphify's "worked examples").** Run brainny on a real session, write a `review.md`: what it kept, what it missed, what it over-captured. This is the only test that catches taste failures.

> **First real test = dogfood on the conversation that designed brainny.** It genuinely produced reusable techniques (two-pass capture, the two-contracts rule, stats-proposes/AI-adjudicates). Capturing them by hand into `entries.json` and running `brainny capture` is the perfect seed entry — the tool's first memory is the memory of its own design.

---

## 7. How the seed grows (roadmap = the growth axis, applied to the project itself)

- **v0 · seed** — `schema.py` + the capture prompt + manual `entries.json` + `graph.json` write + a dead-simple terminal tree. *Test:* capture one real session by hand; Layer 1 green.
- **v0.1 · sprouting** — `stats.py` (local embeddings, neighbors, novelty band, recurrence, decay), `dedup.py`, `neglected`. *Test:* Layers 2–3 green.
- **v0.2** — `viz.py` `graph.html`, git hook (rebuild/summarize on commit). *Test:* Layer 6 smoke.
- **v0.3** — `serve.py` MCP + proactive `surface_precautions`. *Test:* Layer 5 giant + trigger firing.
- **v0.4 · mature** — `central.py`, asymmetric sync, cross-project connections. *Test:* multi-project dedup.
- **v1 · harvested** — `brainny install` across platforms, publish to PyPI. *Test:* Layer 7 review reads clean.

**Do next:** build `schema.py`, drop the §3 prompt into `skills/brainny/SKILL.md`, hand-capture this design session, and run the v0 path end to end. Smallest loop that proves the whole shape.
