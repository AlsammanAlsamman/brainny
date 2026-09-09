# brainny — sync-check skill (session-start, permission-gated)

Runs once, at the very start of a session, per the "brAInny ambient
capture" section of the user's global `~/.claude/CLAUDE.md`. This is
**not** the ~25-minute catch loop — it fires once per session and then
stops; do not re-run it later in the same session.

## What this replaces

The original plan (`OPERATIONS.md` step 7) wanted a truly durable
"every 2-3 days" background trigger. Neither available mechanism supports
that: `CronCreate` is session-only, and the `schedule` skill's cloud
routines can't reach local files at all. This skill is the practical
substitute — piggyback on whenever a session actually starts, check
cheaply, and ask before doing anything, rather than trying to force a
timer that can't exist for this architecture.

## What to do

1. If the `brainny` CLI isn't installed/on PATH: do nothing, silently.
2. Run `brainny status` from the current project's directory.
3. Read the output:
   - `central folder: not configured` → nothing to do, stop silently.
     Don't suggest setting one up — that's the user's call, unprompted.
   - `central copy: not synced yet` → drift (never synced).
   - `central copy: N idea(s) at ... (in sync)` → no drift, stop silently.
   - `central copy: N idea(s) at ... (+K idea(s) since last sync)` → drift.
4. If there's no drift, or no central folder configured: say nothing, do
   nothing further this session.
5. If there **is** drift, ask the user once, in plain chat (not a tool
   popup) — something like:
   `brainny: N idea(s) here haven't synced to central yet — run` `` `brainny sync` `` `now?`
   Then wait for their reply like any normal question.
6. Only on a clear yes, run `brainny sync` from the project directory.
   Never add `--push` yourself — if they also want the GitHub push, that's
   still a separate, explicit ask (`brainny sync --push`), per the
   asymmetric/never-silent-push rule in `SEED.md` §1.7. Report the command's
   own output back to them.
7. On no / no reply / any other answer: drop it. Do not ask again later in
   this same session. It's fine to ask again next session if drift still
   exists then.

## What this must never do

- Never run more than once per session.
- Never push to GitHub on its own initiative.
- Never touch any project other than the one the current session is in.
- Never treat silence or an ambiguous answer as consent.
