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

9. First-run onboarding: the `brainny-onboarding` skill. ✅
   - Added after the fact, not in the original plan — a real user (not
     the maintainer) installing brainny for the first time had no way to
     discover `central-folder`/GitHub sync short of reading `README.md`.
     Same pattern as steps 3/6's ambient skills, but the guard is
     "at most once, ever, per machine" rather than per-session or
     looped: it checks `onboarding-done` in `~/.brainny/config.json`
     first and does nothing at all once that's set, regardless of the
     answer given.
   - Only actually asks anything when both `onboarding-done` and
     `central-folder` are unset. Asks two things via `AskUserQuestion`:
     where the central folder should live (home dir / Documents /
     custom — never guessed), and whether to back it with a GitHub repo
     (walking through installing a portable `gh` CLI without admin
     rights and a token-based, non-browser login if needed) or stay
     local-only.
   - New `onboarding-done` config key in `brainny/config.py`.
   - Dogfooded for real, not just read: invoked live on the maintainer's
     own machine (which genuinely had neither key set), correctly
     detected the fresh-install state, asked both questions, and set
     `central-folder` to the chosen path. Confirmed `brainny sync`
     afterward actually populates that folder — onboarding only points
     config at it, it never pushes anything itself.
   - Caught a related gap this surfaced: `brainny-out/` (the tool's own
     dogfooded ideas) had been committed into brainny's own repo the
     whole time, which is confusing for a fresh clone — untracked it
     (`.gitignore` + `git rm --cached`) since it's per-project local
     data, same as in any project that uses brainny.

10. User-directed capture: the `brainny-catch-this` skill. ✅
    - The other two capture skills (`/brainny` full review, `/brainny-catch`
      ambient) decide *for* the user what's worth keeping. There was no way
      for the user to just say "capture that specific thing I'm pointing
      at" without waiting for the ambient loop to maybe notice it in its
      next ~25-min pass, or manually hand-writing an `entries.json`.
    - Originally named `/brainny-save`; renamed to `/brainny-catch-this` so
      the naming reads clearly alongside the ambient `/brainny-catch` it's
      the directed sibling of.
    - `/brainny-catch-this <description>` searches the *whole* session (not a
      recent window — the user may be pointing at something from much
      earlier), and treats the user's request itself as having already
      cleared the "is this worth keeping" bar — no ambient gate to
      second-guess it, unlike catch/full-review. It always responds
      (title + kind captured, or "couldn't find that, say more"), unlike
      the ambient skills' silence-by-default.
    - Dogfooded live: invoked with a real description
      ("the technique for visually verifying colored terminal/ANSI output
      by converting it to HTML and screenshotting with headless Chrome"),
      correctly found that technique in the session, wrote it up, and
      captured it as `idea_0023`.

11. Proactive recall: `brainny recall` + the `brainny-recall` skill. ✅
    - Every skill up to this point only *captures*. Nothing fed captured
      knowledge back into a *new* session — a precaution learned in one
      project never resurfaced when starting similar work in another,
      unless the user remembered to run `brainny search` themselves. This
      is genuinely the missing half of the tool's value (see the
      "is brainny useful at all" discussion this step came out of): a
      well-organized journal you have to remember to read isn't a memory
      that resurfaces itself.
    - New CLI command `brainny recall <term> [term...]` (OR-matched):
      searches the current project's own `graph.json` *and* every other
      project synced into the configured central folder, labeling each
      hit with its source project so a cross-project match (the
      interesting case) is obviously not local. Falls back to local-only
      search with a clear note when no central folder is configured.
      Covered by 3 new tests (local-only, cross-project, no-match) —
      60 tests total now.
    - New skill `brainny-recall`: fires once per session, right after the
      user's *first* substantive message (not before — nothing to match
      against yet; not on every message — too noisy). Pulls a few
      concrete keywords out of that message, runs `brainny recall`, and
      — using real judgment, not raw keyword-match — mentions anything
      genuinely relevant before proceeding with the task, naming the
      source project when it's a cross-project hit. Silent when nothing
      relevant turns up, same silence-by-default discipline as catch.
    - Verified for real against the maintainer's actual central folder
      (`brainny recall pip windows` correctly surfaced 8 real precautions
      captured earlier in this same session/project). Not yet verified:
      the skill's own auto-trigger firing on a *fresh* session's first
      message — same caveat as every other ambient skill here, since this
      session's CLAUDE.md was already loaded before the edit landed.

12. `brainny open --central`. ✅
    - Real gap, found by a real user hitting it: `brainny open` only ever
      looked at `./brainny-out/graph.html` in the current directory, with
      no path to the central folder at all — even with one fully
      configured, there was no way to open it short of navigating to
      `<central>/<project>/graph.html` by hand.
    - `brainny open --central` opens `<central-folder>/<project>/
      graph.html` instead, where `<project>` defaults to the current
      directory's inferred project name, or an explicit `--project <name>`
      (works from *anywhere*, including a directory with no local
      `brainny-out/` at all — e.g. straight from the home directory).
      Clear, distinct errors for each failure mode: no central folder
      configured, no project name inferable, or that project never
      synced yet (points at `brainny sync`).
    - 4 new tests (not configured, no central copy yet, inferred project,
      explicit `--project`) — 64 tests total. Verified for real too, from
      both the project directory and cold from the home directory
      (`C:\Users\...>` with no local graph at all), matching exactly the
      scenario that surfaced the gap.

13. Cloning an existing central brain + real daily push cadence. ✅
    - Two gaps in the same conversation: onboarding could only ever
      *create* a new central folder — a second machine, or a fresh
      install meant to pick up an *existing* central brain from GitHub,
      had no path in. And `sync-interval-days` (step 2's config key) was
      pure documentation — nothing in the code ever read it; there was
      no real "every N days, push to GitHub" mechanism at all, despite
      the original step-7 intent.
    - `brainny config set-central <path> --clone <url>` (new `cli.py`
      flag): clones an existing central repo instead of creating an
      empty folder — refuses to clone into a path that already exists
      and isn't empty, so it can't silently clobber something. Every
      project previously synced there from any machine becomes
      immediately visible via `brainny recall`/`search`/`open --central`.
    - `brainny status` now reports real push staleness when the central
      folder is a git repo: `central github: last pushed X day(s) ago
      (push every Y day(s))`, flagged `- due for a GitHub push` once
      `sync-interval-days` (now genuinely read from config, defaulting
      to **1 day**, down from the old documented-only "3") has elapsed
      since the central folder's last commit.
    - `brainny-onboarding` gained a fork: brand-new central brain (as
      before) vs. "I already have one" (asks for the URL + where to
      clone it to, same concrete-location-choices discipline as before).
      `brainny-sync-check` now checks *two* independent things each
      session start — local drift (as before) and GitHub push
      staleness — and can ask about either or both, but a yes to one
      is never treated as consent for the other (still asymmetric-push
      safe, `SEED.md` §1.7).
    - 5 new tests (clone downloads and is usable, clone refuses a
      non-empty target, status shows no push line when central isn't
      git, status shows "not due" right after a push, status flags a
      backdated commit as "due") — 69 tests total. Verified for real:
      `brainny status` against the maintainer's actual (non-git, local-
      only) central folder correctly shows no push-staleness line at
      all, matching the local-only choice made during onboarding.

14. The `origin` field: human / AI / collaborative, filterable. ✅
    - Everything up to this point captured *what* was learned but not
      *who* originated it. The user's framing: humans supply direction
      and innovation, the AI supplies collective/pattern knowledge, and
      a lot of real work is genuinely both — collapsing that distinction
      loses something real about how brainny's knowledge actually forms.
    - New `Origin = Literal["human", "ai", "collaborative"]` on
      `EntryInput`/`Node` (`brainny/schema.py`), `Optional[...] = None` —
      missing/old entries read as "unclassified" (an honest fourth
      state), never defaulted to a guessed value.
    - Capture-skill rules, not a coin flip: `/brainny-catch-this` is
      always `"human"` by construction (the user just told you what to
      capture — that *is* the human-origin signal, regardless of who
      wrote the underlying code). `/brainny-catch` and the full
      `/brainny` review make a real per-entry judgment call, preferring
      `"collaborative"` over guessing a side when genuinely mixed.
    - The dashboard: a pill-button filter (All / Human / AI /
      Collaborative / Unclassified) in the header, driving a single
      `filteredData()` applied consistently to the itemized list, both
      graph views, and every Stats tab number/chart — not a separate
      filter per view. Idea nodes now carry an origin-colored ring
      (kind fill stays the same); the "promising" highlight moved from
      stroke color to stroke width so the two signals don't collide.
      Added a "by origin" bar chart in Stats next to "by kind".
    - Reconciled a real drift found along the way: the project-local
      `skills/brainny/catch.md` (nominally the "source of truth" per its
      own global mirror's header note) had fallen behind the actually-
      running global copy — missing the "which project this captures
      into" section entirely. Brought local back in sync with what was
      really running before adding the origin-judgment instructions on
      top, rather than building on the stale version.
    - 4 new schema tests (each origin value accepted, invalid value
      rejected, default is `None` not a guess) — 73 tests total.
      Verified visually with headless Chrome: tagged the real local
      graph with varied origins, screenshotted every view (list, both
      graph views, Stats) to confirm the filter actually narrows every
      one of them consistently, then restored the real data to its
      honest `null`/unclassified state (these 24 ideas predate the
      field — they were never actually re-judged, so leaving them
      unclassified is the truthful choice, not a cosmetic default).

15. The `skill` kind + attachments: `brainny attach` and `brainny-catch-skill`. ✅
    - Prior kinds (technique/precaution/solution/insight) are all prose —
      a description of what to do, with nothing to literally follow. The
      user's framing: some things discussed during a session are genuinely
      reusable *procedures* (how a Snakemake project should be structured,
      the GWAS QC steps, how a specific plot should be built), and the
      thing that makes a procedure actually reusable later — by a human or
      an AI — is real evidence attached to it, not just a paragraph: a
      script, a small illustrative table, a small plot.
    - New `Kind` value `"skill"` (`brainny/schema.py`) — distinguished from
      `"technique"` by having actual evidence attached, not just richer
      prose; the schema docstring spells out the distinction so future
      capture skills judge it consistently.
    - New `Attachment` model (`type: "code"|"plot"|"table"`, `filename`,
      optional `description`) and `attachments: list[Attachment]` on
      `EntryInput`/`Node`. Attachments are never embedded as binary content
      in `graph.json` (SEED.md §1.6's two-contracts rule still holds) —
      only the filename is recorded there; the actual file lives under
      `brainny-out/attachments/<idea-id>/`.
    - New CLI command `brainny attach <idea-id> <file> --type
      code|plot|table [--description ...] [--rename ...] [--session ...]`:
      validates the idea id exists and the file exists, enforces a
      **2 MB** cap (`MAX_ATTACHMENT_BYTES` in `cli.py`) so evidence stays
      "enough to guide," not a copy of the real dataset/output, copies the
      file in, appends the `Attachment` record plus a `growth_log` entry,
      and updates `last_touched`. `brainny sync` now also copies the whole
      local `attachments/` tree into the central folder's copy, same
      project→central-only direction as everything else it syncs.
    - New skill `brainny-catch-skill`, the fourth capture mode alongside
      `/brainny`, `/brainny-catch`, and `/brainny-catch-this`:
      `/brainny-catch-skill <description>` — same user-directed,
      always-responds contract as `/brainny-catch-this` (search the whole
      session, `origin` always `"human"`), but captures `kind: "skill"`
      and walks the conversation for real evidence to attach via
      `brainny attach` after the initial capture returns the new idea's
      id, rather than fabricating a placeholder when nothing suitable
      exists.
    - Dashboard: each attachment shows as a small colored "sign" badge
      (code / plot / table) next to the idea's title in the itemized list,
      and as a linked row (with an inline thumbnail for `plot` type) in
      the expanded body — `<img>`/`<a>` against the relative
      `attachments/<id>/<filename>` path, which resolves fine over
      `file://` for a static `graph.html` even though a `fetch()`/XHR
      would be CORS-blocked. New `"skill"` entry in `KIND_COLOR`/
      `KIND_ICON` (`brainny/viz.py`) so skill ideas render distinctly from
      techniques everywhere kind already drives color.
    - 10 new tests (4 schema: skill kind accepted, attachments accepted,
      invalid attachment type rejected, empty filename rejected; 6 CLI:
      unknown idea id rejected, missing file rejected, oversized file
      rejected, attach copies file + updates graph, `--rename` honored,
      sync copies attachments to central) — 83 tests total.

16. Inline `snippet` field — evidence without a file. ✅
    - `brainny attach` (step 15) covers evidence that's genuinely a file,
      but a lot of what's worth keeping verbatim during a session is
      already just text: a short code excerpt, an equation, a config
      block, a table's column-by-column structure described in words. The
      user's ask: give brainny the freedom to keep that directly on the
      idea/skill itself, not force everything through a file + `attach`.
    - New `snippet: Optional[str]` on `EntryInput`/`Node`
      (`brainny/schema.py`), capped at `MAX_SNIPPET_CHARS` (4000) — small
      enough to guide, same discipline as attachments; if it doesn't fit,
      it belongs in a real attached file instead of being truncated down.
      Deliberately free-form (no language/type field) — it's meant for
      code, equations, or structure notes alike, whatever fits the idea.
    - Rendered in the dashboard's itemized list as a monospace `<pre>`
      block in the expanded body (preserves whitespace/newlines, unlike
      `detail`'s plain paragraph), plus a small pencil "sign" badge next to
      the title alongside the code/plot/table attachment badges — visible
      at a glance that an idea has something to literally read, without
      opening it.
    - `brainny search`/`brainny recall` now search `snippet` text too
      (`cli.py`'s haystacks), so a precaution or skill carrying, say, an
      equation is findable by matching content inside it, not just its
      title/summary.
    - All four capture skills (`SKILL.md`, `catch.md`, `catch-this.md`,
      `catch-skill.md`) updated to know about `snippet` and when to reach
      for it vs. a real `brainny attach`ed file — the dividing line is
      simply size/nature: pasteable text goes in `snippet`, an actual file
      (a whole script, a real image, a real table file) goes through
      `attach`.
    - 3 new schema tests (snippet accepted, defaults to `None`, oversized
      snippet rejected) — 86 tests total.

17. Automatic project → central mirroring on every capture/attach. ✅
    - Real gap, found by a real user hitting it: they'd been working in
      another project for a while and its ideas simply weren't showing up
      in the central folder. Root cause, confirmed by checking the actual
      central folder directly: that project had captured locally many
      times but never once run `brainny sync` — sync was fully manual
      (step 3/13), and the once-per-session `brainny-sync-check` nudge
      only fires at session *start*, so ideas captured mid-session (the
      common case) went un-synced until the *next* session started, and
      even then only if the user said yes to the ask. Central existing
      and working correctly (it does, since step 3 — onboarding, central
      folder, `brainny sync`, `brainny recall`, GitHub push cadence are
      all real and tested) doesn't help if nothing ever tells it about a
      given project's ideas.
    - SEED.md §1.7 already says "Project → central: always" — the gap was
      that "always" was being satisfied by an opt-in command, not
      actually happening on every capture. Fixed to match the letter of
      that line: new `_sync_to_central()` helper in `cli.py`, called
      automatically at the end of both `cmd_capture` and `cmd_attach`
      (when a central folder is configured; silent no-op otherwise, so a
      fresh install with nothing configured yet behaves exactly as
      before). `cmd_sync` refactored to reuse the same helper — it still
      exists, now mainly for backfilling ideas captured before a central
      folder existed, and for `--push`, its only GitHub-touching job.
      Still local-disk-only, still never touches git on its own — the
      "Central → project: only on explicit request, never auto-committed"
      half of §1.7 is completely unaffected; only the project → central
      direction got tightened.
    - Caught and fixed a real bug this introduced along the way: several
      existing `attach` tests didn't use the `isolated_config` fixture
      (fine before this change, since attach never touched config), so
      once attach started auto-mirroring, those tests started writing
      into whatever central folder is configured on the machine actually
      running the suite — confirmed this had already happened to the
      maintainer's own real `~/brainny-central` (a stray `p/` project
      directory from a test run). Cleaned up the polluted real folder and
      made `isolated_config` `autouse=True` for the whole test module so
      this class of bug can't recur silently.
    - 4 new CLI tests (capture doesn't mirror when no central configured,
      capture mirrors and matches node count when central is configured,
      two captures in a row keep the central copy in sync end-to-end
      confirmed via `brainny status` showing "(in sync)", attach mirrors
      too) — 90 tests total. Verified for real against the maintainer's
      actual central folder: captured and attached with central
      configured, confirmed the mirror lands immediately without a
      separate `brainny sync` call, then confirmed the real folder was
      clean of test pollution afterward.

18. Vendor D3 inline — graph.html no longer depends on a CDN. ✅
    - Real gap, found by a real user hitting it: they synced 4 ideas to
      central successfully, confirmed the data was genuinely in
      graph.json, but `graph.html` still rendered blank when opened.
      Traced it to `<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/
      dist/d3.min.js">` — the page depended on fetching D3 from a CDN at
      *view* time, and if that fails (offline, a firewall/proxy blocking
      that host, or just a flaky network at the moment the file happens
      to be opened) the page loads with the data sitting right there in
      it but nothing ever gets drawn, no visible error either. This
      directly contradicted this file's own docstring/README claim of
      being a "static, self-contained, git-shareable file."
    - Fixed by vendoring D3 v7.9.0 (same version that was pinned via CDN)
      into `brainny/vendor/d3.v7.9.0.min.js` (+ `D3_LICENSE.txt`,
      ISC-style, ~280&nbsp;KB) and baking its source directly into the
      generated HTML (`viz.py`'s `_D3_JS`, loaded once at import time,
      same `</` escaping already used for the embedded data block) in
      place of the CDN `<script src>` tag. `graph.html` genuinely has
      zero network dependency now — it renders identically offline,
      behind a firewall, or years from now regardless of what's still
      reachable online. `pyproject.toml` gained
      `[tool.setuptools.package-data]` so the vendored file actually
      ships in a real (non-editable) `pip install`, not just this dev
      checkout.
    - Updated the one existing test that had been asserting the CDN URL
      was present (`test_render_html_cdn_references` →
      `test_render_html_embeds_d3_with_no_cdn_dependency`) to instead
      assert no `cdn.jsdelivr.net`/`<script src=` remains and D3's own
      version-banner comment is actually embedded — 90 tests total
      (unchanged count; this replaced a test rather than adding one).
      Verified for real, reproducing the exact failure: rendered a fresh
      dashboard and screenshotted it with headless Chrome launched with
      `--host-resolver-rules="MAP * 0.0.0.0"` (every external host
      unreachable, matching the user's blank-page scenario) — the graph
      drew correctly with real data, confirming the fix under the actual
      failure condition, not just "the tests still pass." Regenerated and
      re-synced this repo's own dogfooded `graph.html` (local + central)
      with the fix afterward.

19. `brainny central` — the actual merged, one-place-to-look central brain. ✅
    - Real gap, surfaced by a real user pushing back on step 17's "central"
      language: "we have foreach project a brain and we have a central
      one" — their mental model (matching SEED.md §0/§2's own "per-project
      graph + a central cross-project graph") was always a single unified
      view, not a folder you have to open one project's subfolder at a
      time. What existed through step 17 (onboarding, auto-mirror sync,
      `brainny recall`) gave real cross-project value but never a single
      merged *dashboard* — exactly the gap the user was naming.
    - New `brainny/central.py`: `list_central_projects()` (every immediate
      subfolder of the central folder with its own `graph.json`) and
      `build_merged_graph()` (concatenates every synced project's nodes
      into one `Graph`, node ids left untouched — see the module's own
      docstring for why: they're only unique within one project's file,
      and a merged Graph doesn't need to rewrite them, since the dashboard
      derives its own DOM-safe key client-side). Deliberately NOT the full
      v0.4 `central.py` from SEED.md's roadmap (dedup, cross-project
      connections) — that needs a real semantic judgment call per SEED.md
      principle #1, not a naive merge; doing it half-right here would be
      worse than being honest that it isn't built yet. SEED.md §7 updated
      to say so explicitly.
    - New CLI command `brainny central` (summary: idea count per synced
      project) / `--html` (writes one merged dashboard to
      `<central-folder>/graph.html`) / `--open`.
    - `viz.py` gained project-awareness for this to render sensibly: each
      node's `project` (from its own `provenance[0].project`) flows into
      the payload; a server-rendered `project` dropdown (only emitted when
      more than one project is actually present, mirroring how the origin
      filter behaves) narrows `filteredData()` the same way origin already
      does, so it applies consistently across the item list and both graph
      views. The itemized list gains a project-heading layer above the
      existing per-domain grouping in this multi-project case. A new
      `itemKey()` gives each idea a DOM/d3-safe identity
      (`"<project>::<id>"`) distinct from its real `id` — necessary
      because two different projects both number their own ideas
      `idea_0001`, `idea_0002`, ... independently, so raw ids collide once
      merged; attachment links still resolve against the real id + project
      folder (`"<project>/attachments/<id>/<filename>"`), since that's
      what's actually on disk.
    - Along the way, `brainny central`'s own summary caught a genuine,
      pre-existing data-hygiene bug in the maintainer's real dogfood data:
      5 ideas physically sitting in this repo's own `brainny-out/`
      actually carry `provenance.project: "sle-hispanic-gwas"` — clearly
      captured for a different (GWAS/Snakemake) project while `brainny
      capture` happened to be run from this repo's directory instead.
      `brainny central` now detects and prints this class of mismatch
      automatically (folder vs. the idea's own provenance disagreeing) so
      it's visible without hand-inspecting `graph.json` — flagged to the
      user rather than silently "fixed," since moving someone's real
      captured ideas between projects is a data decision only they should
      make.
    - 16 new tests (`tests/test_central.py`: 5 for `list_central_projects`/
      `build_merged_graph`, including the "ids collide across projects,
      must not be silently dropped" case; `tests/test_cli.py`: 6 for the
      `central` command's summary/`--html`/`--open` paths plus the
      provenance-mismatch diagnostic) — 101 tests total. Verified for real
      against the maintainer's actual central folder: ran `brainny central
      --html`, confirmed the printed summary (28 ideas, 2 synced folders,
      the 5-idea provenance mismatch correctly flagged), then screenshotted
      the merged dashboard with headless Chrome — project dropdown showing
      **3** projects (not 2 — it derives from real provenance, not folder
      names, so the misattributed "sle-hispanic-gwas" ideas show up as
      their own filterable group even though they were never synced as
      their own folder), item list correctly grouped project-then-domain.

Each step should land, get tested, and get dogfooded (per SEED.md §6
Layer 7) before the next starts — same discipline as the v0 build.
