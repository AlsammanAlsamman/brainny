# project-nature — profiler prompt

Produces/refreshes the one-line PROJECT NATURE descriptor that
`prompts/capture.md` (Pass 1) reads to decide what counts as reusable in
this project.

## Procedure
1. Look at the project: its files, README, recent sessions — whatever is
   already in context. Do not go fetch things that aren't already visible.
2. Write ONE line in the form:
   `"<what this project is>; reusable = <the kinds of things worth keeping here>"`

   Examples:
   - "web app / TypeScript + React; reusable = code patterns, gotchas, config"
   - "brand design; reusable = layout systems, type/color rules, critique heuristics"
   - "contract review; reusable = clauses, argument structures, red-flag checks"
   - "long-form writing; reusable = outlines that worked, voice notes, structure"
3. Store it wherever the calling project keeps that kind of note (e.g. a
   `PROJECT_NATURE` line in `brainny-out/`, or the top of the session log).
   brainny itself does not prescribe the storage location for v0 — the
   capture prompt just needs the line available when it runs.

## When to refresh
Re-run this whenever the project's shape has materially changed — a new
stack, a pivot in what the work is, a new domain entirely. Otherwise reuse
the last descriptor; it doesn't need to be regenerated every session.
