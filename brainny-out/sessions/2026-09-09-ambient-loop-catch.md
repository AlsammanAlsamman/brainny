# session: ambient-loop-catch (2026-09-09)

Raw provenance log for the session that built OPERATIONS.md §6 steps 4-6:
central folder config + local sync, GitHub sync (`--push`, confirmation-
gated), and the ambient `/brainny-catch` loop itself — installing it as a
real global Claude Code skill (`~/.claude/skills/brainny-catch/`) and
wiring the standing CLAUDE.md rule.

This entry is itself the first live firing of `/brainny-catch` as a real
installed skill (invoked directly to prove the skill file loads and
behaves correctly, right after installing it) — applying its own gate to
the recent slice by hand, same dogfooding discipline as step 3.

Two items cleared the gate: a git upstream-tracking gotcha that broke a
step-5 test fixture, and a genuine, just-observed-firsthand Claude Code
operational fact (the skills list refreshes mid-session, no restart
needed). Everything else in steps 4-6 (the sync command design, the
config.py reuse, the --push confirmation gating) was either already
captured earlier or judged not non-obvious enough to clear the bar.
