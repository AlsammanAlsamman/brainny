# brainny — onboarding skill (one-time, ever)

Runs once, at the start of a session, per the "brAInny ambient capture"
section of the user's global `~/.claude/CLAUDE.md` — but only in the
specific circumstance described below. Unlike `/brainny-catch` (every
~25 min) and `brainny-sync-check` (once per session), this runs **at most
once per machine, ever**.

## When to actually do anything

1. If the `brainny` CLI isn't installed/on PATH: do nothing, silently.
2. Run `brainny config get onboarding-done`. If it prints `true`: do
   nothing, silently, for the rest of time. This is the only guard that
   matters long-term — it's what makes this safe to check every session
   without becoming a nag.
3. Run `brainny config get central-folder`. If it's already set: do
   nothing, but still run `brainny config set onboarding-done true` (no
   need to ask — they've already set this up some other way, e.g. by
   hand or in another project).
4. Only if `onboarding-done` is unset AND `central-folder` is unset:
   proceed to the offer below.

## The offer

This is a one-shot, low-pressure offer — not a blocking setup wizard.
Ask the user directly in chat (or via a tool like `AskUserQuestion` if
available in this environment), roughly:

> brainny can keep a shared "central" brain that collects ideas from
> every project on this machine, not just this one (see `brainny sync`).
> It's entirely optional. Want to set one up now?

If they decline (no / not now / maybe later / no answer): run
`brainny config set onboarding-done true` and stop. Do not ask again
this session or any future one. They can always run
`brainny config set-central <path>` by hand later — mention that once,
briefly, then drop it.

If they say yes, ask two things (one message, or `AskUserQuestion` with
two questions is fine):

1. **Where.** Offer concrete default options rather than an open-ended
   "type a path": something like `~/brainny-central` (home directory) or
   `~/Documents/brainny-central` (Documents), plus the option to name a
   custom path. Don't guess silently — the whole point is that this asks.
2. **GitHub-backed or local-only.** Whether they also want it pushed to
   a GitHub repo (so it syncs across machines / is durably backed up),
   or kept purely local for now. Local-only is a completely fine answer.

## Executing the choice

1. Run `brainny config set-central <chosen-path>`. This creates the
   folder and points every future `brainny sync` at it (see
   `brainny/config.py` / `cli.py`'s `cmd_config`/`cmd_sync` — it never
   overwrites an existing folder's contents, just points at it).
2. If they want it local-only: done. Run
   `brainny config set onboarding-done true` and tell them in one line
   what you did and that `brainny sync` from any project will now push
   there.
3. If they want it GitHub-backed, walk them through it — don't assume
   `gh` is installed or authenticated:
   - Check `gh --version`. If missing, you (the assistant) can install
     a **portable** copy without admin rights: download the CLI's own
     zip release (`Invoke-WebRequest` + `Expand-Archive` on Windows, or
     the equivalent tarball on macOS/Linux) rather than an installer
     that needs elevation — installers requiring UAC/sudo elevation can
     silently fail in a non-interactive shell.
   - Check `gh auth status`. If not logged in, you cannot complete a
     browser OAuth flow yourself (no browser access) — tell the user to
     either run `gh auth login --web` themselves in their own terminal,
     or generate a personal access token at
     `https://github.com/settings/tokens/new` (repo scope) and run
     `gh auth login --with-token` themselves (keep the token out of the
     chat transcript — it's a credential).
   - Once authenticated, create the repo: `gh repo create <name>
     --private --source <central-path> --remote origin` (default to
     **private** unless they say otherwise), or ask if they'd rather
     create the empty repo on github.com themselves and give you the
     URL — either is fine.
   - `git init` the central folder if `gh repo create --source` didn't
     already, commit whatever's there, and do the initial push.
   - Run `brainny config set onboarding-done true`.
4. Report back in a few short lines what got set up (path, and whether
   it's GitHub-backed) — this is a one-time, visible setup event, not an
   ambient/silent action like catch or sync-check.

## What this must never do

- Never ask more than once, regardless of the answer.
- Never invent a path or create a GitHub repo without the user choosing
  that path/that GitHub option first — always ask, per the user's
  explicit requirement that this "should ask the user."
- Never make the repo public without being told to.
- Never block other work in the session on this — if the user seems
  busy or mid-task when this would fire, it's fine to ask briefly and
  move on to whatever they actually came to do; this isn't urgent.
