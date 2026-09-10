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

## Note: local drift should now be rare

`brainny capture` and `brainny attach` auto-mirror to the central folder
on every call now (OPERATIONS.md step 17) — local drift mostly only
happens for ideas captured before a central folder was configured, or on
an older `brainny` build. This skill still checks for it (belt-and-
suspenders, and it's the only thing that catches those backfill cases),
but expect it to fire far less often than the GitHub-push-staleness half.

## What to do

1. If the `brainny` CLI isn't installed/on PATH: do nothing, silently.
2. Run `brainny status` from the current project's directory.
3. Read the output for **two independent things** — either, both, or
   neither can apply:
   - **Local drift** (this project → central folder):
     - `central folder: not configured` → nothing to check here.
     - `central copy: not synced yet` → drift (never synced).
     - `central copy: N idea(s) at ... (in sync)` → no drift.
     - `central copy: N idea(s) at ... (+K idea(s) since last sync)` → drift.
   - **GitHub push staleness** (central folder → its git remote), only
     printed at all when the central folder is a git repo:
     - `central github: last pushed X day(s) ago (push every Y day(s))`
       → up to date, nothing to do.
     - `... - due for a GitHub push` → the central folder has gone
       longer than `sync-interval-days` (default 1) since its last
       commit — it may have unpushed local commits, or just nothing new
       from anyone in a while; either way it's due for a check.
4. If neither applies: say nothing, do nothing further this session —
   the common, correct outcome.
5. If **local drift** exists, ask once, in plain chat (not a tool
   popup):
   `brainny: N idea(s) here haven't synced to central yet — run` `` `brainny sync` `` `now?`
6. If the central folder is **due for a GitHub push** (regardless of
   whether step 5 also fired — combine into one message if both apply),
   ask:
   `brainny: the central folder hasn't been pushed to GitHub in over a day — run` `` `brainny sync --push` `` `now?`
   This is still just an ask — never run `--push` without a clear yes,
   per the asymmetric/never-silent-push rule in `SEED.md` §1.7. If the
   user already said yes to a plain `brainny sync` in step 5 *and* a
   GitHub push is also due, you can fold it into one command
   (`brainny sync --push`) instead of running sync twice — use judgment,
   don't make them answer the same question twice for one outcome.
7. On no / no reply / any other answer to either question: drop it. Do
   not ask again later in this same session. It's fine to ask again next
   session if either condition still holds then.

## What this must never do

- Never run more than once per session.
- Never push to GitHub without an explicit yes to that specific
  question — a yes to the local-sync question alone does not imply
  consent to push.
- Never touch any project other than the one the current session is in.
- Never treat silence or an ambiguous answer as consent.
