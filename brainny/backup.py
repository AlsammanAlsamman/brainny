"""Off-machine backup of the central folder: a private GitHub repo and/or a
Google Drive (or any cloud-synced) folder, pushed on a fixed cadence
(default every 72 hours) and only when there is actually something new.

This is the opt-in exception to "never push silently" (SEED.md §1.7):
the user turns it on once, deliberately, with `brainny backup setup`,
which records `backup-auto: true`. After that, every capture/attach (and
an optional OS-level scheduled task, `brainny backup schedule`) calls
`maybe_auto_backup()`, which does nothing unless the cadence has elapsed
AND the central folder changed since the last backup. Without `setup`,
nothing here ever runs on its own -- `brainny sync --push` stays the only
other path to a remote, unchanged.

Targets:
- github: the central folder itself becomes a git repo whose `origin` is
  the user's (private) repo. `setup --github URL` does the `git init` /
  `remote add` / first push -- the one place brainny runs those, because
  the user asked for it by URL in that very command.
- drive: the central folder is mirrored (copy, never delete) into a
  folder that Google Drive for desktop -- or OneDrive/Dropbox, it's just a
  path -- syncs. No OAuth, no API: the Drive client does the upload.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from brainny import config

DEFAULT_INTERVAL_HOURS = 72.0
DRIVE_SUBDIR = "brainny-central"
SCHEDULED_TASK_NAME = "brainny-backup"
# A push from inside `brainny capture` must never hang the session on a
# credential prompt or a dead network -- fail fast, report, move on.
GIT_TIMEOUT_SECONDS = 120


def interval_hours() -> float:
    raw = config.get_value("backup-interval-hours")
    try:
        return float(raw) if raw else DEFAULT_INTERVAL_HOURS
    except ValueError:
        return DEFAULT_INTERVAL_HOURS


def targets() -> list[str]:
    found = []
    central = config.get_value("central-folder")
    if central and config.get_value("backup-github"):
        found.append("github")
    if config.get_value("backup-drive-folder"):
        found.append("drive")
    return found


def hours_since_last_backup() -> float | None:
    raw = config.get_value("last-backup")
    if not raw:
        return None
    try:
        last = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last).total_seconds() / 3600


def is_due() -> bool:
    since = hours_since_last_backup()
    return since is None or since >= interval_hours()


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, env=env, timeout=GIT_TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["git", *args], 1, "", f"git {args[0]} timed out after {GIT_TIMEOUT_SECONDS}s")


def _central_root() -> Path | None:
    central = config.get_value("central-folder")
    return Path(central) if central else None


def _fingerprint(root: Path, skip: set[str]) -> str:
    """Cheap change detector for the drive mirror: relative path + size +
    mtime of every file. Good enough to answer "anything new since the
    last backup?" without hashing 20MB of HTML every capture."""
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if rel.parts and rel.parts[0] in skip or not path.is_file():
            continue
        st = path.stat()
        h.update(f"{rel.as_posix()}|{st.st_size}|{st.st_mtime_ns}\n".encode())
    return h.hexdigest()


def _backup_github(central_root: Path) -> tuple[str, str]:
    """Returns (status, message); status is 'pushed', 'unchanged' or 'error'."""
    if not (central_root / ".git").is_dir():
        return "error", f"{central_root} is not a git repo - run `brainny backup setup --github <url>`."
    _git(["add", "-A"], central_root)
    staged = _git(["diff", "--cached", "--quiet"], central_root).returncode != 0
    if staged:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        commit = _git(["commit", "-m", f"brainny backup: {stamp}"], central_root)
        if commit.returncode != 0:
            return "error", f"git commit failed: {commit.stderr.strip() or commit.stdout.strip()}"
    # push even with nothing newly staged: an earlier `sync --push` or a
    # failed backup can leave local commits that never reached the remote
    ahead = _git(["rev-list", "--count", "@{u}..HEAD"], central_root)
    if not staged and ahead.returncode == 0 and ahead.stdout.strip() == "0":
        return "unchanged", "github: nothing new since last backup."
    push = _git(["push", "-u", "origin", "HEAD"], central_root)
    if push.returncode != 0:
        return "error", f"git push failed: {push.stderr.strip()}"
    return "pushed", f"github: pushed to {config.get_value('backup-github')}"


def _backup_drive(central_root: Path) -> tuple[str, str]:
    drive = Path(config.get_value("backup-drive-folder") or "")
    if not drive.is_dir():
        return "error", f"drive folder {drive} doesn't exist (is Google Drive for desktop running?)."
    fp = _fingerprint(central_root, skip={".git"})
    if fp == config.get_value("backup-drive-fingerprint"):
        return "unchanged", "drive: nothing new since last backup."
    dest = drive / DRIVE_SUBDIR
    shutil.copytree(central_root, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git"))
    config.set_value("backup-drive-fingerprint", fp)
    return "pushed", f"drive: mirrored to {dest}"


def run_backup(force: bool = False, quiet: bool = False) -> int:
    """One backup pass over every configured target. `force` skips the
    cadence check (never the "anything new?" check -- an unchanged central
    folder is never re-pushed). Returns a process exit code."""
    say = (lambda msg: None) if quiet else print
    central_root = _central_root()
    found = targets()
    if central_root is None or not found:
        print("brainny: no backup target configured - run `brainny backup setup --github <url>` "
              "and/or `--drive <folder>`.", file=sys.stderr)
        return 1
    if not force and not is_due():
        remaining = interval_hours() - (hours_since_last_backup() or 0)
        say(f"brainny: backup not due yet (next in {remaining:.1f}h; every {interval_hours():g}h). "
            "Use `brainny backup --now` to back up immediately.")
        return 0

    failed = False
    pushed = False
    for target in found:
        status, message = (_backup_github if target == "github" else _backup_drive)(central_root)
        if status == "error":
            failed = True
            print(f"brainny backup: {message}", file=sys.stderr)
        else:
            pushed = pushed or status == "pushed"
            say(f"brainny backup: {message}")
    # Only a pass that actually pushed something restarts the clock: with
    # nothing new, the very next capture after the cadence elapses should
    # still trigger a backup, not wait another full interval.
    if pushed and not failed:
        config.set_value("last-backup", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    return 1 if failed else 0


def maybe_auto_backup() -> None:
    """Hook for capture/attach/propose/sync: back up iff the user opted in
    via `setup`, the cadence elapsed, and something changed. Never raises
    and never fails the calling command -- a backup problem is reported on
    stderr and retried on the next trigger."""
    if config.get_value("backup-auto") != "true" or not targets() or not is_due():
        return
    try:
        run_backup(quiet=False)
    except Exception as exc:  # noqa: BLE001 -- must never break a capture
        print(f"brainny backup: skipped ({exc})", file=sys.stderr)


def setup_github(url: str) -> int:
    central_root = _central_root()
    if central_root is None:
        print("brainny: no central folder configured - run `brainny config set-central <path>` first.", file=sys.stderr)
        return 1
    if not (central_root / ".git").is_dir():
        init = _git(["init", "-b", "main"], central_root)
        if init.returncode != 0:
            print(f"brainny: git init failed: {init.stderr}", file=sys.stderr)
            return 1
        print(f"brainny: initialized git repo in {central_root}")
    remotes = _git(["remote"], central_root).stdout.split()
    _git(["remote", "set-url" if "origin" in remotes else "add", "origin", url], central_root)
    config.set_value("backup-github", url)
    config.set_value("backup-auto", "true")
    print(f"brainny: central folder will back up to {url} (every {interval_hours():g}h, only when changed)")
    print("brainny: make sure that repo is PRIVATE - it holds notes from every project you capture in.")
    return run_backup(force=True)


def setup_drive(folder: str) -> int:
    central_root = _central_root()
    if central_root is None:
        print("brainny: no central folder configured - run `brainny config set-central <path>` first.", file=sys.stderr)
        return 1
    path = Path(folder).expanduser().resolve()
    if not path.is_dir():
        print(f"brainny: {path} doesn't exist - point this at a folder inside your Google Drive "
              "(e.g. 'G:/My Drive'), which Google Drive for desktop syncs.", file=sys.stderr)
        return 1
    config.set_value("backup-drive-folder", str(path))
    config.set_value("backup-auto", "true")
    print(f"brainny: central folder will mirror into {path / DRIVE_SUBDIR} (every {interval_hours():g}h, only when changed)")
    return run_backup(force=True)


def install_schedule() -> int:
    """Durable trigger independent of Claude sessions: an OS task that runs
    `brainny backup` (which itself checks cadence + changes) every 12h, so
    the 72h cadence holds even through weeks with no captures."""
    if sys.platform != "win32":
        print("brainny: add this line to `crontab -e` to check twice a day:")
        print(f"  0 */12 * * * {sys.executable} -m brainny backup")
        return 0
    exe = Path(sys.executable)
    pythonw = exe.with_name("pythonw.exe")  # no console window flashing up
    runner = pythonw if pythonw.exists() else exe
    result = subprocess.run(
        ["schtasks", "/Create", "/F", "/SC", "HOURLY", "/MO", "12", "/TN", SCHEDULED_TASK_NAME,
         "/TR", f'"{runner}" -m brainny backup'],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"brainny: could not create scheduled task: {result.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"brainny: Windows scheduled task '{SCHEDULED_TASK_NAME}' runs `brainny backup` every 12h "
          f"(it only pushes when {interval_hours():g}h have passed and something changed).")
    return 0


def remove_schedule() -> int:
    if sys.platform != "win32":
        print("brainny: remove the `brainny backup` line from `crontab -e`.")
        return 0
    result = subprocess.run(["schtasks", "/Delete", "/F", "/TN", SCHEDULED_TASK_NAME], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"brainny: {result.stderr.strip()}", file=sys.stderr)
        return 1
    print(f"brainny: removed scheduled task '{SCHEDULED_TASK_NAME}'.")
    return 0


def status_line() -> str | None:
    found = targets()
    if not found:
        return None
    since = hours_since_last_backup()
    last = "never" if since is None else f"{since:.1f}h ago"
    auto = "auto" if config.get_value("backup-auto") == "true" else "manual"
    due = " - due (runs on next capture, or `brainny backup`)" if is_due() else ""
    return f"  backup: {', '.join(found)} ({auto}, every {interval_hours():g}h), last {last}{due}"
