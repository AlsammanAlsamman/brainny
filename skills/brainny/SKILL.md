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

Also decide its `origin` — who actually originated this, independent of kind:
- `"human"` — the user did/said/decided it; you're just the one capturing it.
- `"ai"` — you (the assistant) figured it out yourself — a mistake you caught,
  a technique you landed on — without the user directing it.
- `"collaborative"` — genuinely built together, back and forth.
This matters: the human supplies direction and innovation, the AI supplies
collective/pattern knowledge, and telling them apart is what makes the
distinction between "what I decided" and "what the model already knew"
visible later. Make the call per entry; don't default to one side out of
convenience, and prefer `"collaborative"` over a guess if it's genuinely
mixed.

### Pass 2 — project-blind seed catcher (recall)
Ignore the project's nature entirely. Look for the tangent — the "huh, that's
interesting and unrelated" moment, the off-topic spark. Do NOT classify or place
it. Emit it as `kind: seed`. Bias toward flagging; time will sort it out. Still
set `origin` the same way as pass 1 if it's reasonably clear whose tangent it
was; leave it unset only if you genuinely can't tell.

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
Emit a JSON array of entries matching the schema in `brainny/schema.py`
(`EntryInput` — may be empty `[]`), write it to a file, then shell out:
```
brainny capture <path-to-entries.json> --project <project-name> --session <session-id>
```
For each entry fill: kind, title, summary (in the user's own reusable terms),
detail (optional), domain/tags, origin (human/ai/collaborative — see above),
and — for precautions — a `trigger` describing WHEN brainny should
proactively surface it ("starting a METAL/GWAS run"). Leave id, embedding,
edges, novelty, recurrence, state, and provenance timestamps EMPTY — the
body fills those.
