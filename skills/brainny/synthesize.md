# brainny — synthesize skill (AI-proposed combinations)

Every other capture skill (`/brainny`, `/brainny-catch`, `/brainny-catch-this`,
`/brainny-catch-skill`) captures ideas one at a time. This one looks across
ideas *already captured* — in this project, possibly over many sessions —
for genuine combinations: sets of ideas that support each other toward
something bigger than any one of them alone. A tool. A website. A
statistical module. A business idea. Something else entirely.

This is SEED.md principle #1 ("statistics propose; the AI adjudicates") at
its purest — there is no deterministic signal for "do these ideas actually
combine into something real." It's a pure semantic judgment call, made by
you, not computed.

You run when the user types `/brainny-synthesize` (optionally with a focus
hint, e.g. `/brainny-synthesize anything GWAS-related`).

## What to look at

Read the current project's actual captured ideas — run `brainny query`
(or read `brainny-out/graph.json` directly) rather than relying only on
what's in this session's own context, since a genuine combination may
span ideas captured across many past sessions, not just this one.

## What counts as a real opportunity

- **At least two ideas** that genuinely reinforce or complete each other
  — not just ideas that happen to share a `domain` tag. Sharing a domain
  is necessary, not sufficient.
- A concrete shape: what would combining them actually produce? Be
  specific — "a GWAS/PRS toolkit for admixed populations" is a real
  answer; "some GWAS stuff" is not.
- One of: `tool`, `website`, `statistical-module`, `business-idea`, or
  `other` if it's real but doesn't fit those.

## The GATE (apply hard — same discipline as every other capture skill)

Default answer is NO. Most passes over a project should propose **zero**
opportunities — that's correct, not a miss. Only propose one when:
- the combination is genuinely coherent (you could describe what it
  *is*, not just what it's "related to"), AND
- it's non-obvious enough that the user wouldn't already have noticed it
  themselves just by skimming the domain list.

Never manufacture an opportunity to have something to report. An empty
pass is a normal, correct outcome, same as `/brainny-catch` finding
nothing.

## Weight — be honest, not persuasive

`weight` (0.0–1.0) is your own genuine confidence that this combination
is real and worth pursuing — not a sales pitch, not inflated to make the
opportunity look better. A shaky, speculative combination should score
low (0.2–0.4); a combination you'd actually bet on scores high
(0.7–0.9). Reserve anything above 0.9 for something you're genuinely
confident about, not just enthusiastic about.

## Output

For each opportunity, fill exactly the fields in `brainny/schema.py`'s
`OpportunityInput`: `title`, `kind`, `weight`, `summary` (what combining
these would actually produce, in plain terms), `idea_ids` (the real,
existing ids from this project's `graph.json` — **at least two**, and
they must actually exist; `brainny propose` rejects ones that don't),
and `rationale` (optional — why these specific ideas support each other,
one or two sentences). Do not set `id` or `created` — the body fills
those.

Write the JSON array (possibly empty — that's fine) to a file, then
shell out from the current project's directory:
```
brainny propose <path-to-opportunities.json> --project <project-name> --session <session-id>
```

Report back what got proposed — title, kind, and weight for each — so
the user can see your reasoning, same as `/brainny-catch-this` always
responds rather than going silent. If you proposed nothing, say so
plainly and briefly explain why nothing cleared the bar, rather than
just going quiet (this is a direct, user-invoked request, not an
ambient pass — silence here would read as broken, not as "nothing
found").

## What this must never do

- Never invent idea ids that don't exist in the project's graph.
- Never propose a combination just because ideas share a domain or tag
  — that's necessary, not sufficient.
- Never inflate `weight` to make an opportunity look more promising than
  you actually believe it is.
- Never `git push` or touch the central folder directly — `brainny
  propose` already mirrors to the configured central folder the same
  way `capture`/`attach` do (project → central, always, on disk only);
  pushing to GitHub stays a separate, explicit `brainny sync --push`.
