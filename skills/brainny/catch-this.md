# brainny — catch-this skill (user-directed capture)

The third capture mode, alongside the full end-of-session `/brainny` review
and the ambient `/brainny-catch` loop. Both of those decide *for* the user
what's worth keeping. This one is the opposite: the user tells you
*exactly* what to capture, in their own words, right now.

You run when the user types `/brainny-catch-this <description>` — for
example:

```
/brainny-catch-this the retry/backoff approach we just built for the API client
/brainny-catch-this that gotcha about stale .done markers in Snakemake
/brainny-catch-this the argument structure I used for the liability clause pushback
```

The `<description>` is the anchor. It may be a topic, a paraphrase, a title,
or just "that thing we talked about 10 minutes ago" — whatever the user gives
you is what you match against the conversation.

## How this differs from the ambient `/brainny-catch`

|                        | `/brainny-catch` (ambient)         | `/brainny-catch-this` (this one)   |
|------------------------|-------------------------------------|-------------------------------------|
| Triggered by           | a timer / the user, no topic        | the user, always with a topic       |
| Scope                  | last ~25 min of conversation only   | wherever in the session matches the description — search back as far as needed |
| The GATE               | default NO, strict, ambient guess   | the user already decided this is worth keeping — your job is to capture it *well*, not to re-litigate whether it's worth keeping |
| Silent on no match?     | yes, always                         | no — this was explicitly asked for; always respond |
| Multiple entries?       | whatever the recent slice yields    | usually one, matching the description; more only if the description clearly covers several distinct ideas |

## What to do

1. If the `brainny` CLI isn't installed/on PATH: say so plainly and stop —
   this is an explicit user request, not an ambient action, so silence is
   wrong here.
2. Find the part(s) of the conversation the description points at. Search the
   whole session, not just a recent window — the user may be pointing at
   something from much earlier.
3. If you can't find anything in the conversation matching the description:
   say so and ask them to paste or describe it more, rather than guessing or
   inventing content. Never fabricate an entry from the description alone if
   the substance isn't actually in the conversation.
4. If you find it, draft one entry (or a small handful, only if the
   description genuinely spans multiple distinct ideas) per the schema in
   `brainny/schema.py` (`EntryInput`): `kind`, `title`, `summary`, `detail`
   (optional), `domain`, `tags`, `trigger` (precautions only). Use the
   project's `PROJECT_NATURE` descriptor the same way `/brainny`/
   `/brainny-catch` do (infer one silently if none exists yet).
5. Still use real judgment on `kind` and phrasing — the user telling you
   *what* to capture doesn't mean you skip making it well-formed and
   actually reusable-reading, same quality bar as the other two skills'
   output. If what they're pointing at is really several loosely related
   things, ask which one they mean rather than mashing them into one vague
   entry.
6. Write the entry/entries to a file, then shell out (from the current
   project's directory):
   ```
   brainny capture <path-to-entries.json> --project <current-project-name> --session <session-id>
   ```
7. Report back what got captured — title(s) and kind(s) — so the user can
   confirm it's the right thing. This is the one capture mode that should
   always produce a visible response, since it's a direct request, not an
   ambient pass.

## What this must never do

- Never invent or embellish content beyond what's actually in the
  conversation — the description points at real material, it doesn't
  supply it.
- Never silently do nothing when asked — if nothing matches, say that.
- Never `git push` or touch the central folder — same as the other capture
  skills, this only writes to the current project's local `brainny-out/`.
- Never skip asking for clarification when the description is ambiguous
  between multiple distinct things in the conversation.
