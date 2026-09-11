# brainny — propose-check skill (session-start, ambient, silent-unless-found)

Runs once per session, per the "brAInny ambient capture" section of the
user's global `~/.claude/CLAUDE.md` — the ambient sibling of the manual
`/brainny-synthesize` skill, the same relationship `/brainny-catch` has
to the full `/brainny` review. This is **not** a loop; it fires once
near session start and then stops for the rest of that session.

## Why this exists

Opportunities (`brainny propose`) don't get proposed unless someone
runs `/brainny-synthesize` on purpose — which means a project's ideas
can sit there, genuinely combinable, for a long time with nobody ever
noticing, simply because nobody happened to ask. This skill closes that
gap: every session gets one free look, automatically, without the user
having to remember to ask for it.

## What to do

1. If the `brainny` CLI isn't installed/on PATH: do nothing, silently.
2. If this exact check has already run once this session for this
   project (regardless of outcome): do nothing — never re-run.
3. Run `brainny status` (or `brainny query`) for the current project. If
   it has fewer than 2 captured ideas total, there's nothing that could
   possibly combine — stop silently.
4. Otherwise, run the same judgment `/brainny-synthesize` does — read
   the project's actual captured ideas (`brainny query` /
   `brainny-out/graph.json`), not just this session's own context, since
   a genuine combination may span ideas captured across many past
   sessions. Apply the exact same GATE and `weight` honesty discipline
   documented in `skills/brainny/synthesize.md` — don't relax it just
   because this run is ambient; a fabricated or inflated-weight
   opportunity is worse than none, ambient or not.
5. If nothing clears the bar (the common, correct outcome most of the
   time): say **nothing** — no "checked, found nothing," same silence
   discipline as `/brainny-catch`. This is the one place this skill's
   contract differs from `/brainny-synthesize`'s: that one always
   responds because it's a direct request; this one is ambient, so
   silence on a null result is correct, not broken.
6. If one or more opportunities genuinely clear the bar: write them the
   same way `/brainny-synthesize` does and shell out
   `brainny propose <path> --project <name> --session <session-id>`,
   then say so — one or two lines is enough (title, kind, weight per
   opportunity) — this is new information the user hasn't seen, so it
   should surface, just tersely.

## What this must never do

- Never run more than once per session, regardless of outcome.
- Never lower the GATE or inflate `weight` just because nothing else is
  competing for the user's attention right now — same honesty bar as a
  manually-requested run.
- Never touch any project other than the one the current session is in.
- Never `git push` or touch the central folder directly beyond what
  `brainny propose` already does on its own (project → central, on disk
  only, same as `capture`/`attach`) — pushing to GitHub stays a
  separate, explicit `brainny sync --push`, never triggered from here.
- Never report "checked, nothing found" — silence is the correct signal
  for a null result, exactly like `/brainny-catch`.
