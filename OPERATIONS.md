# brAInny — OPERATIONS

> Companion to `SEED.md`. SEED.md is the capture/dedup/graph *engine* —
> this doc is how that engine actually gets invoked, automated, packaged,
> and branded in day-to-day use. Same spirit as SEED.md: a living doc,
> worked through one numbered step at a time, thinning down to code as
> each step lands.

---

## 0. The two modes brAInny runs in

- **Manual** — the user types a `brainny <command>` (or a `/brainny`-style
  skill invocation) in a session, on purpose, right now.
- **Ambient** — once configured, brAInny runs *passively* in the
  background of every Claude Code session: a standing habit, not
  something the user has to remember to invoke. This is the "screen the
  discussion every 20–30 minutes" behavior.

Both modes end up calling the same underlying CLI (`brainny/cli.py`) —
ambient mode is just *what triggers* the call, not a different tool.

---

## 1. Command surface

### Existing (v0, already built)
- `brainny capture <entries.json> --project <name> --session <id>`
- `brainny query` / `brainny query --html`

### New: `brainny catch` (the lightweight ambient command)
The CLI itself can never "catch the last few messages" on its own — per
SEED.md's architecture, only the assistant (Part 1) can see the session;
the CLI (Part 2) only ever reads a JSON file handed to it. So `catch` is
really **a new, lighter skill** (`skills/brainny/catch.md`, a trimmed
sibling of the existing capture skill) paired with the *same*
`brainny capture` CLI verb underneath:

- Looks only at the last ~20–30 minutes of conversation (not the whole
  session) — cheap, low-friction, safe to run unattended.
- Same GATE as full capture (reusable + non-obvious), but single-pass —
  ambient runs are frequent, so recall is less critical per-run; the
  full two-pass review still happens at end-of-session (`/brainny`).
- Silent no-op is the common case (per SEED.md §3: "most sessions yield
  0–2 entries" — most 20-minute windows yield **zero**). It should not
  narrate "nothing found" every cycle; only speak up when it captures
  something.

### Suggested additions (your ask: "commands you can suggest")
- `brainny status` — idea count, last capture time, central-sync state,
  whether a central folder is configured. The first thing to run when
  you forget what state things are in.
- `brainny config get|set <key> <value>` — central folder path, GitHub
  remote, sync cadence, the project-nature descriptor.
- `brainny sync` — manual trigger for the local↔central / GitHub sync
  described in §3 (also runs automatically on the 2–3 day cadence).
- `brainny open` — open `graph.html` (or its dashboard successor) in the
  default browser without hand-typing the path.
- `brainny search <term>` — grep captured ideas by keyword/tag/kind.
- `brainny recent [--days N]` — what's been captured lately; the
  low-effort version of `query` for "what did I just catch."
- `brainny doctor` — environment/config sanity check (central folder
  reachable? git remote valid? stale lockfile? — a `brew doctor` for
  brAInny).

(Already on the roadmap per SEED.md §7, unchanged by this doc: `grow`,
`neglected`, `install`, `serve`, `hook`.)

---

## 2. Ambient scanning (every 20–30 minutes, by default)

**Mechanism**: Claude Code's own primitives, not a custom daemon —
- `/loop` (dynamic self-pacing) to fire the `catch` skill on an interval
  within a running session, **or**
- a durable rule in the user's global `CLAUDE.md` that tells *every*
  session to self-schedule this at start-up (`ScheduleWakeup` /
  `/loop 25m catch`-equivalent) — the same pattern the user's CLAUDE.md
  already uses for `hpc-cluster-ops` ("load this automatically, don't
  wait to be asked").

**Why CLAUDE.md and not a hook**: a hook (e.g. `SessionStart`) fires once
per session start reliably; getting a *recurring* 20–30 min cadence
needs the loop/schedule machinery, which is prompt-driven, not a raw
settings.json hook. So the concrete plan is: add a standing rule to the
user's global `CLAUDE.md` (via the `update-config` skill) instructing
Claude to kick off a dynamic loop running the `catch` skill near the
start of any session, mirroring the existing HPC-ops rule's structure.

**Guardrail**: ambient catch must stay silent-by-default (per §1) and
must never take destructive or user-visible actions beyond writing to
`brainny-out/` — no git push, no messages sent, nothing that needs
approval, so it can safely run unattended.

---

## 3. The central place (local + optional GitHub)

- `brainny config set-central <path>` points at a folder — could be a
  bare local directory or a git repo. Stored in `~/.brainny/config.json`
  (matches SEED.md's `central.py` / `~/.brainny/global.json` plan).
- **Project → central: always** (every local capture also lands centrally
  the next sync). **Central → project: only on explicit request** — this
  is SEED.md §1.7's asymmetric-sync rule verbatim; a shared team repo
  must never silently receive another project's private ideas, and a
  project must never silently receive someone else's ideas either.
- If the central folder has a GitHub remote, `brainny sync` stages,
  commits, and pushes. **This needs your explicit sign-off before it's
  ever wired to run unattended** — pushing to GitHub is a "affects shared
  systems" action, so the every-2–3-days automatic trigger should ask
  first the first several times, and only skip asking if you explicitly
  opt into a durable "sync without asking" setting. I won't wire silent
  auto-push by default.
- The "every 2–3 days Claude will be asked by brainny" cadence is a
  second, longer-period scheduled check (via the `schedule` skill —
  proper cron, not a loop kept alive by one open session) that runs
  `brainny sync` and, once it exists, the cross-project dedup pass
  (`dedup.py`, v0.1+).

---

## 4. Packaging as a real Python module + CLI

- Already true today: `pyproject.toml` defines `brainny = brainny.cli:main`,
  and `pip install -e .` gives a global `brainny` command on PATH (this
  is how every command in this whole project has been run).
- Remaining for a "real" release:
  - `brainny --version` and a proper `--help` (argparse gives `--help`
    for free already; version needs wiring to `__version__`).
  - Decide: stay install-from-source (`pip install git+...` /
    `pipx install <path>`), or actually publish to PyPI. SEED.md §5
    already flags "verify name free on PyPI" as unresolved — worth
    checking before committing to that path.
  - A one-line installer story for a fresh machine (`pipx install
    brainny` or equivalent) so "make it a python module" is true for
    someone who isn't in this repo.

---

## 5. ASCII brand banner

Shown on bare `brainny` / `brainny --help`, and optionally atop
`graph.html`. Two ingredients:
- A small, recognizable ASCII **pictogram** echoing `assets/logo.jpg`
  (a literal photo-to-ASCII conversion of a generated image usually reads
  as noise at terminal width — better to hand-design a simple glyph in
  the same spirit: a tree/brain motif, since that's the actual mark).
- A figlet-style **wordmark** for "brAInny" underneath/beside it.

This step needs a quick look at the actual logo together before locking
the glyph design in — flagged here rather than guessed.

---

## 6. Suggested build order ("one by one")

1. ✅ ASCII banner + `--version` — small, immediate, no architecture risk.
   `brainny/banner.py`; bare `brainny` and `brainny --help` show it,
   `--version` stays terse/scriptable. Color auto-disables for non-TTY
   output or `NO_COLOR`. The glyph itself is derived from
   `assets/assci.txt` (an image-to-ASCII render of `assets/logo.jpg`),
   cropped to just the brain graphic and downsampled with a majority-vote
   filter (sharper edges than averaging for line art) — the baked-in
   pixel-text wordmark in the source was dropped in favor of our own
   typed wordmark, which stays legible at banner scale.
2. ✅ New pure-CLI commands: `status`, `config`, `search`, `recent`, `open`
   (no new moving parts, just CLI surface on data that already exists).
   `config` added `brainny/config.py` — a small `~/.brainny/config.json`
   read/write layer (`central-folder`, `github-remote`,
   `sync-interval-days`, `project-nature` keys); nothing reads or syncs
   through it yet, that's steps 4-5. `status` already reports central
   folder state via it. 12 new tests, all isolated from the real
   `~/.brainny` via a `DEFAULT_CONFIG_DIR` monkeypatch fixture.
3. ✅ `catch` skill + wiring to `brainny capture` (the ambient-capture
   unit, but still manually invoked at this stage — triggered by typing
   `/brainny-catch`, not yet by the standing loop from step 6).
   `skills/brainny/catch.md` + `prompts/catch.md`: recent-slice-only,
   single pass (project-aware precision, no project-blind sweep), silent
   when nothing qualifies, a one-line non-blocking receipt when something
   is caught, never re-flags what this session already caught. Dogfooded
   for real on this very session (§6 Layer 7 discipline): applying its
   own gate by hand caught 2 precautions (a Python late-binding default-
   argument gotcha that had been silently polluting real `~/.brainny`
   config through the "isolated" step-2 tests, and the Windows
   pinned-cwd directory-lock behavior from the folder rename) —
   `idea_0009`/`idea_0010` in `brainny-out/graph.json`.
4. ✅ Central folder config + `sync` — local-only, no GitHub yet.
   `brainny config set-central <path>` validates the path (rejects a
   file, creates a missing directory) and stores it via step 2's
   `config.py`. `brainny sync` pushes the *current local graph* to
   `<central>/<project>/{graph.json,graph.html}` — always local→central,
   never the reverse (SEED.md §1.7's asymmetric-sync rule; a pull command
   is deliberately not built here). Project name is inferred from the
   local graph's own provenance (`--project` overrides it). Reuses
   `graph.save_graph`/`viz.save_html` as-is — the central folder is just
   another `out_dir`, no new storage format. `status` now also reports
   whether the central copy is in sync or drifted (`+N idea(s) since last
   sync`). Verified end-to-end against a real (scratch) central folder:
   set-central → sync → status "in sync" → new local capture → status
   correctly shows the drift. 8 new tests, all isolated from real
   `~/.brainny`.
5. ✅ GitHub sync (`brainny sync --push`) — with confirmation gating per
   §3. brainny never runs `git init` or `git remote add` itself — it only
   ever pushes to a git repo + remote the user already set up in the
   central folder. Pushing only happens with `--push` for that run, or
   the durable `git-auto-push: true` setting; without either, a git
   remote's presence is just reported, never used. Scoped `git add
   <project>/` (not the whole central repo), skips the commit when
   nothing changed (`git diff --cached --quiet`), surfaces real
   commit/push failures verbatim rather than swallowing them. **Claude-
   level rule** (not enforced by the code): when an AI session decides to
   run `--push` (or set `git-auto-push`) on the user's behalf, it should
   still ask first — the flag is the gate for direct CLI use, not a
   license for an agent to push unattended. Verified end-to-end against a
   real local bare repo standing in for GitHub (not mocked): `sync`
   alone stays local and reports the remote; `sync --push` actually
   commits+pushes (confirmed via `git log` on the bare repo); a second
   `--push` with no changes correctly no-ops; `git-auto-push` correctly
   skips the flag requirement. 7 new tests, all against real temp git
   repos, none touching the real `~/.brainny` or this project's own repo.
6. ✅ Ambient auto-scan every ~25 min (the CLAUDE.md standing-loop rule).
   Two parts, since `/brainny-catch` needed to be reachable from *any*
   project, not just this repo:
   - `~/.claude/skills/brainny-catch/SKILL.md` — a global install of this
     repo's `skills/brainny/catch.md` (that repo copy stays the source of
     truth; re-sync the global one if they drift).
   - A new "brAInny ambient capture" section in the user's global
     `~/.claude/CLAUDE.md`: at the start of every session, in every
     project, check `brainny --version` silently; if present, start a
     recurring loop (`Skill({skill: "loop", args: "25m /brainny-catch"})`);
     if not, skip silently. Guardrails carried over verbatim from the
     skill: silent-when-empty, writes only to the *current* project's
     local `brainny-out/`, never `git push`, never re-reviews the whole
     session.
   - Scope decision (asked, not assumed): every session in every project,
     not just brainny-aware ones — matches the original ask exactly, at
     the cost of a `brainny-out/` folder appearing in whatever project
     first captures something.
   - Trigger decision (asked, not assumed): a true wall-clock timer via
     `ScheduleWakeup`/the `loop` skill, not activity-piggybacking — closer
     to "screens every 20-30 minutes" even though it means every session
     periodically wakes up for as long as it runs.
   - **What's actually verified vs. not**: `brainny` confirmed callable
     from a totally unrelated directory (not just this repo) and confirmed
     to create `brainny-out/` correctly wherever it's run from. The
     skill file itself was proven live — installing it made it
     immediately invokable in *this already-running* session (no restart
     needed, confirmed via the skills list updating mid-session), and
     invoking it directly applied its own gate to the recent conversation
     for real, caught 2 entries, and shelled out to `brainny capture`
     correctly (`idea_0011`/`idea_0012`). What's **not** yet confirmed:
     whether a *fresh* session actually reads the new CLAUDE.md rule and
     self-starts the loop on its own — that can only be proven by
     starting one, since this session's CLAUDE.md was already loaded
     before the edit landed.
7. The 2–3 day scheduled reconciliation trigger. ✅ (redefined — see
   below; original cloud/cron scoping turned out not to be buildable, see
   the finding underneath).
   - Redefined as a **session-start, permission-gated check** instead of
     a true background timer, since neither candidate mechanism can
     actually deliver "every 2-3 days" for this architecture (see
     finding below). Piggybacks on the fact that `brainny status` already
     detects drift by comparing local vs. central idea counts — no new
     detection logic needed, just a skill that reads that output and
     asks before acting.
   - New skill `skills/brainny/sync-check.md` (+ global install at
     `~/.claude/skills/brainny-sync-check/SKILL.md`, same
     mirror-with-source-of-truth-note pattern as the catch skill): runs
     once at session start (not on the 25-min loop), parses
     `brainny status`'s central-copy line, and if it's anything but
     `(in sync)` or "not configured", asks the user in plain chat before
     running `brainny sync`. Silent otherwise. Never adds `--push` on its
     own initiative — that's still a separate explicit ask, same as
     `brainny sync --push` always was.
   - Wired into `~/.claude/CLAUDE.md`'s "brAInny ambient capture" section
     alongside the existing catch-loop bullet, with its own guardrails
     (silent when nothing to sync, at most one ask per session, never
     treats silence as consent).
   - Verified the exact status strings the skill's instructions key off
     of (`in sync`, `not synced yet`, `+N idea(s) since last sync`)
     against `tests/test_cli.py`'s existing status assertions (lines
     ~273/286) rather than assuming the wording — they match exactly.
     Not yet verified: an actual fresh session self-triggering this at
     startup (same caveat as the catch loop's step 6 note — this
     session's CLAUDE.md was already loaded before the edit landed).
8. Packaging/PyPI polish. ✅
   - PyPI name `brainny` confirmed free (`pypi.org/pypi/brainny/json` →
     404) and dated in this file's own project-structure listing and in
     `SEED.md`.
   - Added `LICENSE` (MIT) and wired `license = { file = "LICENSE" }`,
     `authors`, `keywords`, and `classifiers` into `pyproject.toml`.
   - `README.md` got a new `## Installation` section spelling out
     install-from-source now vs. `pip install brainny` once actually
     published — publishing itself stays a separate, explicit,
     not-yet-made decision (SEED.md §5).
   - Verified with a real install, not just reading the TOML:
     `pip install -e ".[dev]"` + `pytest tests/ -q` (55 passed, no
     regressions) + `pip show brainny` reflecting the new author/license
     metadata.

**Step 7 finding (resolved by redefinition, see step 7 above):**
investigated the two candidate mechanisms directly rather than assuming
either would work. `CronCreate` is session-only — it dies with the
session and caps at 7 days, so it can't be the "every 2-3 days" trigger
regardless of session lifetime. The `schedule` skill's cloud routines are
durable, but they run in an isolated cloud sandbox with **no access to
local files, local services, or local environment variables** — only a
specified GitHub repo URL. A cloud routine could only ever act on a
central folder that's a real GitHub remote (untested, not set up), and
even then there's nothing substantive to reconcile yet since
`dedup.py`/`stats.py` (v0.1, roadmap only) don't exist. Rather than build
something hollow around infrastructure that fundamentally can't reach the
user's local machine, step 7 was redefined to a session-start,
permission-gated local check — see above.

Each step should land, get tested, and get dogfooded (per SEED.md §6
Layer 7) before the next starts — same discipline as the v0 build.
