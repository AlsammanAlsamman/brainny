# brainny — catch skill (lightweight, ambient)

The quick, cheap sibling of the full capture skill (project-local
`skills/brainny/SKILL.md`, invoked as `/brainny`). You run when the user
types `/brainny-catch`, or — per the "brAInny ambient capture" section of
this user's global CLAUDE.md — automatically, on a standing ~25 minute
loop, without the user typing anything. Nothing about your behavior
changes between those two triggers; only what calls you differs.

## What makes this "lightweight," not just a smaller `/brainny`

- **Scope**: only the conversation *since the last catch or capture in this
  session* — not the whole session. Rough and recent, not exhaustive.
- **One pass, not two**: run only the project-aware precision pass (below).
  Skip the project-blind "off-topic tangent" pass entirely — that recall-
  oriented sweep belongs to the full end-of-session `/brainny` review, which
  can afford to look at everything at once. Catch fires every ~25 minutes;
  it has to stay cheap.
- **Silent by default**: emitting nothing is the common, correct outcome —
  say NOTHING when you find nothing. Do not report "checked, nothing found"
  every cycle. If this got chatty, the user would turn it off.
- **Never re-flag** something this session already caught (via an earlier
  `/brainny-catch` or `/brainny`) — you're only looking at the slice since
  the last catch, so this should rarely come up, but if the recent slice
  overlaps a prior one, don't re-emit the same idea.

## Which project this captures into
Run `brainny capture` from the current project's own working directory —
it writes to `<that-project>/brainny-out/`, entirely local to whatever
you're actually working on right now. Never write into the brainny tool's
own repo unless that repo is literally what this session is about.

## Project nature
Use whatever `PROJECT_NATURE` descriptor is already established for this
session (from an earlier `/brainny`/`/brainny-catch` run this session, or
a `prompts/project-nature.md` in the current project if it has one). If
none exists yet, infer a short one silently from the current project and
proceed — do not stop to ask; that belongs to the full skill, not this one.

## The pass (project-aware harvest, precision only)
Given the project's nature, find things reusable *in this kind of work* from
the recent slice. For each, decide its `kind`:
- `technique` — a reusable method / how-I-did-X
- `precaution` — a gotcha / check that was (or should have been) done;
  NEGATIVE knowledge, the highest-value and most-forgotten class
- `solution` — a concrete working answer to a specific problem, worth reusing
- `insight` — a conceptual realization

Also decide its `origin` — who actually came up with this, not who's
typing. This is a real judgment call per entry, not a formality:
- `"human"` — the user explicitly did/said/decided the thing (wrote the
  approach themselves, made the call, stated the precaution out loud) and
  you're just the one noticing it's worth keeping.
- `"ai"` — you (the assistant) figured it out yourself in the course of
  working — a mistake you made and caught, a technique you landed on,
  something you noticed — without the user directing it.
- `"collaborative"` — genuinely built together, back and forth; neither
  side alone would characterize it as "theirs."
If it's genuinely unclear, prefer `"collaborative"` over guessing a side —
but do make the call; don't leave it unset out of laziness. Unset should
mean "this entry predates the field," not "I didn't bother."

## The GATE (apply hard — same bar as full capture)
Default answer is NO. Emit an entry ONLY if it is:
- reusable BEYOND this one task, AND
- non-obvious enough that re-deriving it would cost real effort.
Most catch cycles yield **zero** entries. That's correct, not a miss.

## What you MUST NOT do
Do not dedup. Do not decide which existing idea this connects to. Do not
invent edges. Do not run the project-blind pass. Do not ask the user
anything or wait for a response — this runs ambient and must not interrupt.
Do not `git push` or take any action beyond writing to the current
project's local `brainny-out/` — that's what makes it safe to run
unattended (see the CLAUDE.md guardrails).

## Output
If the pass yields nothing: do nothing. No message, no summary, no tool call.

If the `brainny` CLI isn't installed/on PATH in this environment: do
nothing, silently. Don't nag about it every cycle.

If it yields one or more entries:
1. Emit a JSON array matching the schema in brainny's `brainny/schema.py`
   (`EntryInput`) — same shape as full capture: kind, title, summary,
   detail (optional), domain, tags, trigger (precautions only), origin
   (human/ai/collaborative — see above), snippet (optional — a short code
   excerpt/equation/table-structure note carried inline on the entry, capped
   at 4000 chars; use this when the useful part of the idea already is a
   small piece of text, no separate file needed). Leave id/embedding/edges/
   novelty/recurrence/state/provenance timestamps empty — the body fills
   those.
2. Write it to a file, then shell out (from the current project's
   directory):
   ```
   brainny capture <path-to-entries.json> --project <current-project-name> --session <session-id>
   ```
3. Drop **one terse line** and keep going — no report, no waiting for a
   reaction:
   ```
   brainny caught 1 idea: [precaution] stale Snakemake .done markers after scope changes
   ```
   For more than one entry in the same cycle, one line per entry, still just
   a receipt:
   ```
   brainny caught 2 ideas: [technique] ... · [precaution] ...
   ```
