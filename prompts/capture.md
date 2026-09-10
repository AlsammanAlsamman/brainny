# capture — prompt template

Used at the end of a working session (or on `/brainny`) to produce the
`entries.json` that `brainny capture` consumes. This is the operational
template; the full instructions live in `skills/brainny/SKILL.md`.

## Inputs
- The current session transcript (already in context — nothing to fetch).
- `PROJECT_NATURE`: one-line descriptor of what this project is and what
  counts as reusable here. Produced/refreshed by `prompts/project-nature.md`.
  If missing, infer a short one from the session and say so before proceeding.

## Procedure
1. Run Pass 1 (project-aware, precision) against `PROJECT_NATURE`. Apply the
   GATE — reusable beyond this task AND non-obvious. Default answer is NO.
2. Run Pass 2 (project-blind, recall). Flag any off-topic spark as `kind: seed`
   without classifying or placing it.
3. For each kept item, fill only the prompt-side fields: `kind`, `title`,
   `summary`, `detail` (optional), `domain`, `tags`, `trigger` (precautions
   only), `snippet` (optional). Do not fill `id`, `embedding`, `edges`,
   `novelty`, `recurrence`, `state`, or `provenance` — the body fills those.
   `snippet` is free text carried straight on the entry — a code excerpt, a
   table's column structure, an equation, a config block — whenever the
   useful part of the idea already *is* a small piece of text and doesn't
   need a real file (`brainny attach` is for that: a whole script, a small
   plot image, a real table excerpt as its own file). Capped at 4000 chars
   (`schema.py`'s `MAX_SNIPPET_CHARS`) — if it doesn't fit, it belongs in an
   attached file instead, not truncated to fit here.
4. Write the JSON array (possibly empty) to a file.
5. Run: `brainny capture <path> --project <project-name> --session <session-id>`

## Output shape (one entry)
```json
{
  "kind": "precaution",
  "title": "...",
  "summary": "...",
  "detail": null,
  "domain": "...",
  "tags": ["..."],
  "trigger": "...",
  "snippet": null
}
```
