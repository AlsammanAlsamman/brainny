# catch — prompt template

The lightweight, ambient sibling of `prompts/capture.md`. Produces the same
kind of `entries.json`, but from a small recent slice of the conversation
instead of the whole session, and runs often (manually via `/brainny-catch`
today; automatically every ~20–30 min once OPERATIONS.md §6 step 6 lands).
This is the operational template; the full instructions live in
`skills/brainny/catch.md`.

## Inputs
- The recent slice of the session *since the last catch or capture* —
  not the whole transcript. Rough and recent, not exhaustive.
- `PROJECT_NATURE`: reuse whatever's already established this session; if
  none exists, infer one silently and proceed (don't stop to ask — that's
  the full skill's job, not this one's).

## Procedure
1. Run the project-aware precision pass only (no project-blind pass — that
   recall sweep is reserved for the full end-of-session `/brainny` review).
   Apply the GATE — reusable beyond this task AND non-obvious. Default
   answer is NO. Most cycles yield zero entries; that's correct.
2. Don't re-flag anything this session already caught.
3. For each kept item, fill only the prompt-side fields: `kind`, `title`,
   `summary`, `detail` (optional), `domain`, `tags`, `trigger` (precautions
   only). Do not fill `id`, `embedding`, `edges`, `novelty`, `recurrence`,
   `state`, or `provenance` — the body fills those.
4. If the array is empty: stop here, silently. No message.
5. Otherwise write the JSON array to a file, then run:
   `brainny capture <path> --project <project-name> --session <session-id>`
6. Drop one terse receipt line per entry and keep going — no report, no
   waiting for a reaction. This runs ambient; it must never interrupt.

## Output shape (one entry — identical to full capture)
```json
{
  "kind": "precaution",
  "title": "...",
  "summary": "...",
  "detail": null,
  "domain": "...",
  "tags": ["..."],
  "trigger": "..."
}
```

## Receipt line(s) — the only user-visible output when something is caught
```
brainny caught 1 idea: [precaution] stale Snakemake .done markers after scope changes
```
