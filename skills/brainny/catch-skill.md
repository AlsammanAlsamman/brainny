# brainny — catch-skill skill (user-directed, reusable procedures)

A fourth capture mode, alongside the full end-of-session `/brainny` review,
the ambient `/brainny-catch` loop, and the user-directed `/brainny-catch-this`.
Those three capture *knowledge* — a technique, a precaution, a solution, an
insight. This one captures a *procedure*: a reusable way of doing something
that was worked out during the session, well-formed enough that following it
again should be as good as re-deriving it from scratch — how a Snakemake
project should be structured, how QC for a GWAS run should be done, how a
specific plot should be built.

You run when the user types `/brainny-catch-skill <description>` — for
example:

```
/brainny-catch-skill the way we structured this snakemake project
/brainny-catch-skill the GWAS QC steps we just went through
/brainny-catch-skill how the manhattan plot should be made for this project
```

The `<description>` is the anchor, same as `/brainny-catch-this` — a topic,
a paraphrase, "that thing we just set up." Search the whole session for what
it points at, not just a recent window.

## What makes a "skill" different from a `technique`

A `technique` is a description in prose. A `skill` is that description PLUS
real evidence — an inline `snippet` (a code excerpt, equation, or table
structure kept as text directly on the entry) and/or a `brainny attach`ed
file (a script, a small illustrative table, a small plot) — substantial
enough that a future session (human or AI) can literally follow it, not
just read about it. If the conversation produced no evidence worth keeping
either way, this probably isn't a `skill` — capture it as a `technique` via
`/brainny-catch-this` instead. Ask the user if it's unclear which one fits.

## What to do

1. If the `brainny` CLI isn't installed/on PATH: say so plainly and stop —
   this is explicit, not ambient, so silence is wrong.
2. Find the part(s) of the conversation the description points at. Search
   the whole session, not just a recent window.
3. If nothing in the conversation matches: say so and ask the user to
   describe or paste more, rather than inventing content.
4. Draft ONE entry (rarely more — a skill is usually one coherent procedure)
   with `kind: "skill"`, per the schema in `brainny/schema.py`
   (`EntryInput`): `title`, `summary`, `detail` (the actual steps/structure,
   written so someone could follow them cold), `domain`, `tags`, and
   `snippet` if step 5 below finds inline evidence worth including. Set
   `origin: "human"` — same reasoning as `/brainny-catch-this`: the user
   pointed at this and said "keep it," which is what "human" means here
   regardless of who wrote any underlying code.
5. Look at what the conversation actually produced for this procedure and
   decide what's worth keeping as evidence. Two ways to carry it, pick
   whichever fits the size:
   - **`snippet`** (inline, on the entry itself, no file) — a short code
     excerpt, an equation, a config block, a table's column-by-column
     structure described as text — anything small enough to paste directly.
     Capped at 4000 chars; if it doesn't fit, it belongs in an attached file
     instead, not truncated down to squeeze in.
   - **`brainny attach`** (a real file, copied to disk, 2 MB cap) — when the
     evidence is genuinely a file: the actual script (not just an excerpt),
     a small example plot image, or a real table excerpt saved as its own
     `.csv`:
     - `code` — the actual script/function that does it (e.g. the manhattan
       plot function, the Snakemake `rule` block)
     - `table` — a tiny excerpt showing the expected shape: column names,
       one or two example rows, format notes — never the real dataset
     - `plot` — a small example image of the output (a thumbnail-sized PNG,
       not a publication-res figure)
   A skill entry can carry both, or either alone. If nothing suitable
   exists in the conversation, don't fabricate one — a skill entry with no
   snippet and no attachments is still valid, just weaker; say so to the
   user rather than inventing a placeholder.
6. Write the entry to a file, then capture it:
   ```
   brainny capture <path-to-entry.json> --project <current-project-name> --session <session-id>
   ```
   This prints the new idea's id (e.g. `idea_0031`).
7. For each piece of evidence identified in step 5, save it to a real file
   (if it isn't already one on disk) and attach it:
   ```
   brainny attach <idea-id> <file> --type code|plot|table --description "one line" --session <session-id>
   ```
   The attach command enforces a small size cap (2 MB) and refuses larger
   files — if something doesn't fit, trim it to the illustrative excerpt
   that actually guides future use, not the full output.
8. Report back what got captured: the title, kind, and which attachments
   (with their type) were added — so the user can confirm it's right.

## What this must never do

- Never invent or embellish the procedure beyond what's actually in the
  conversation.
- Never attach a full dataset, a large output file, or a full-resolution
  figure — evidence here means "just enough to guide," per the size cap.
- Never silently do nothing when asked — if nothing matches, say so.
- Never `git push` or touch the central folder — this only writes to the
  current project's local `brainny-out/`, same as the other capture skills.
