<div align="center">

<img src="assets/icon.png" alt="brAInny" width="150" />

# br<font color="#e8b23d">AI</font>nny

**catches your ideas before the wind**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Status: v0 seed](https://img.shields.io/badge/status-v0%20seed-orange.svg)](OPERATIONS.md)

</div>

> **Every session with AI, you invent things you never write down — a
> precaution, a trick, a working fix — and by tomorrow they're gone with
> the wind. brAInny catches them before they blow away, so you can come
> back to any of them later, reuse them instead of re-discovering them,
> and watch what you know actually compound, session after session.**

<p align="center">
  <img src="assets/screenshot-dashboard.png" alt="brAInny dashboard: force-directed network of captured ideas with a colored halo per domain cluster, plus an itemized list alongside" width="100%">
</p>

<p align="center"><sub>Graph tab — force network with cluster halos.</sub></p>

<p align="center">
  <img src="assets/screenshot-stats.png" alt="brAInny dashboard Stats tab: domain treemap, per-cluster activity table, kind breakdown, and newest ideas" width="100%">
</p>

<p align="center"><sub>Stats tab — domain treemap, growth trends, kind breakdown. Both from <code>brainny query --html</code>, on this project's own real, dogfooded ideas.</sub></p>

---

## The problem this solves

You're deep in a task with an AI assistant, solving something else
entirely, and along the way you figure out a trick, hit a gotcha you'll
absolutely hit again, or land on a working approach you're proud of. It
was never the *point* of the session — so it isn't written anywhere. The
session ends, the terminal closes, and it's gone. Weeks later you pay the
same cost to re-learn the same lesson.

**brAInny is not a note app.** It's built specifically to catch that
throwaway residue — the stuff nobody would think to write down on
purpose — and turn it into something durable:

- A **technique** you invented gets saved, so next time it's a lookup,
  not a rediscovery.
- A **precaution** you learned the hard way gets remembered, so you never
  pay for the same mistake twice.
- A **solution** to a fiddly problem stays reachable, so future-you can
  just reuse it.
- A stray **insight** that isn't useful yet gets kept as a seed — if it
  keeps coming back across sessions, brAInny notices and lets it grow.

It works for anyone who works with AI, not just developers — a
precaution, a structure, a working approach is the same shape of thing
whether you write code, contracts, prose, or research.

---

## How it works, in one picture

```
[ your AI session ]
        │  a lightweight skill watches for reusable moments and emits them
        ▼
   brainny capture           ← the CLI: validates, dedups, files it
        ▼
  brainny-out/graph.json     ← your durable, growing memory for this project
        │
        ├── graph.html       interactive dashboard — browse, search, revisit
        └── (optional) sync to one shared "central" brain across all your projects
```

Nothing runs on a server, nothing leaves your machine unless you
explicitly point it at a central folder — and even then, syncing to
GitHub is a separate, explicit command, never silent.

**Not locked to one AI.** The brain (the `brainny` CLI + `graph.json`) is
plain, assistant-agnostic Python — the skills in `skills/brainny/` are
just markdown instructions plus shell commands. The ones built and tested
so far target Claude Code, but nothing about the design is Claude-only:
any assistant that can read an instruction file and run a shell command
can drive brainny the same way.

---

## Install

```bash
git clone https://github.com/AlsammanAlsamman/brainny
cd brainny
pip install -e ".[dev]"
```

That puts a `brainny` command on your PATH — usable from **any** project
directory, not just this repo — plus the importable `brainny` package.
(Not published to PyPI yet — the name is confirmed free, publishing is
just a deliberate later step.)

`python -m brainny` and `python -m brainny.cli` both work too, from any
directory (including the parent of your clone).

**Windows note.** With the Microsoft Store build of Python, the `Scripts`
directory that receives `brainny.exe` is often *not* on `PATH` — pip prints a
`WARNING: The script brainny.exe is installed in '…\PythonXX\Scripts' which is
not on PATH`. Add that `…\Scripts` folder to your user `PATH` (or just run
`python -m brainny`).

---

## Use it

**1. Capture something reusable**, by hand or via the assistant skill:

```bash
brainny capture path/to/entries.json --project myproj --session s1
```

(`prompts/capture.md` shows the shape of an entry. In Claude Code, the
`skills/brainny/` skills do this for you — see below.)

Or, mid-session, just point at it: **`/brainny-catch-this the retry
approach we just built for the API client`** — searches the whole session
for whatever you describe (not just a recent window), and always tells you what it
captured. Unlike the ambient skills below, this one doesn't second-guess
whether it's worth keeping — you already decided that.

**2. See what you've kept:**

```bash
brainny status              # counts, domains, last capture, sync state
brainny query                # your ideas as a terminal tree
brainny query --html          # a browsable dashboard: brainny-out/graph.html
                                #   Graph tab: radial tree / force network, click-to-inspect
                                #   Stats tab: domain treemap, growth trends, kind breakdown
brainny open                  # open that dashboard in your browser
brainny open --central          # ...or the central folder's copy of this project instead
brainny open --central --project X  # ...or an explicit project's central copy, from anywhere
brainny search "docker"        # find anything by keyword, tag, domain, kind
brainny recall retry api client  # search THIS project + every project in your central folder
brainny recent --days 7          # what you've captured lately
```

**3. Let it capture itself, ambiently.** Install the skills once
(`skills/brainny/*.md`, plus their global counterparts under
`~/.claude/skills/`) and every Claude Code session will:
- **once, ever, per machine** — on the first session after install, if
  no central folder is set up yet, ask whether you want one (and where,
  and whether to back it with GitHub) before ever touching anything;
  never asks again after that, whatever you answered;
- quietly scan the last ~25 minutes of conversation for anything worth
  keeping, and file it without interrupting you — most cycles catch
  nothing, and that's correct;
- once, at the start of the session, check whether anything's drifted
  from your shared central brain and ask before syncing it;
- right after your first message, quietly check whether anything you've
  captured before — in *this* project or any other one synced to your
  central brain — is relevant to what you're about to do, and mention it
  briefly if so. This is the proactive-recall half: everything else here
  only captures, this is what actually feeds it back to you.

Nothing is ever pushed to GitHub without you asking for it, in that
moment, every time.

**Every Claude Code command brainny adds:**

| Command | Runs | What it does |
|---|---|---|
| `/brainny` | manually, end of a session | full two-pass review of the whole session (project-aware + project-blind); project-local only — copy `skills/brainny/SKILL.md` into a project to use it there |
| `/brainny-catch` | manually, or every ~25 min in the background | lightweight scan of the last ~25 min for anything worth keeping; silent when it finds nothing |
| `/brainny-catch-this <description>` | manually, whenever you point at something | searches the *whole* session for what you describe and captures it; always tells you what it did |
| `/brainny-sync-check` | automatically, once per session | checks for drift against your central folder and asks before syncing |
| `/brainny-onboarding` | automatically, once ever per machine | offers to set up a central folder (and optionally GitHub) on first use |
| `/brainny-recall` | automatically, once per session, after your first message | surfaces anything relevant you've captured before — in this project or any other one — before the task starts |

All but `/brainny` are installed globally, once, and then work in any project.

**4. Optionally, keep one brain across every project** (the onboarding
skill above offers to do this for you on first run — or by hand):

```bash
brainny config set-central ~/brainy-central   # point at a shared folder
brainny sync                                    # push this project's ideas there
brainny sync --push                              # + commit & push, if that folder has a git remote
```

Sync only ever flows project → central. Central never overwrites a
project's own copy unless you explicitly ask for that.

---

## Status

**v0 · seed** — the core loop above is real and tested (64 tests).
Capture *and* proactive recall (`brainny recall` + the `brainny-recall`
skill) both work today. Not yet built: automatic dedup/novelty scoring so
`recurrence`/`state` truly evolve over time, decay for neglected ideas,
and an MCP server for tighter, tool-level AI access (recall today goes
through the CLI via a skill, not a direct protocol). See `OPERATIONS.md`
for the full build order and `SEED.md` for the complete design rationale
— both are as honest about
what's *not* built yet as what is.

---

## Layout

```
brainny/                 the CLI + engine (Python, assistant-agnostic)
skills/brainny/          the capture skills (assistant-facing prompts)
prompts/                 entry + project-nature templates
tests/                   64 tests, see SEED.md §6 for the testing philosophy
brainny-out/             where captures land when you use brainny *on*
                         this repo (gitignored — same as in any project;
                         not shipped, this is per-user local data)
assets/icon.png          brand mark
SEED.md                  the living design doc — read this first
OPERATIONS.md            how it actually runs day to day
```

Read `SEED.md` for the constitution, architecture, and entry schema.
Read `OPERATIONS.md` for the command surface, ambient capture, and the
central/GitHub sync model in full.

## Contributors

| Name | Contact |
|---|---|
| Alsamman M. Alsamman | [aalsamman100@gmail.com](mailto:aalsamman100@gmail.com) |
| Muhammad M. Adeel | [m.muzammal.adeel@outlook.com](mailto:m.muzammal.adeel@outlook.com) |
