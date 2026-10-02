"""`brainny backup`: central folder -> private GitHub repo / Drive folder on
a cadence, only when changed. Real git repos in tmp_path (a bare repo
stands in for GitHub), same as test_cli.py's --push tests."""

from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from brainny import config as config_module
from brainny.capture import capture
from brainny.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    config_dir = tmp_path / "home-brainny"
    monkeypatch.setattr(config_module, "DEFAULT_CONFIG_DIR", config_dir)
    return config_dir


def _run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)


def _bare_log(bare: Path) -> str:
    return _run(["git", "log", "--oneline", "--all"], bare).stdout


@pytest.fixture
def central_with_ideas(tmp_path, capsys):
    central = tmp_path / "central"
    out_dir = tmp_path / "out"
    main(["config", "set-central", str(central)])
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["--out-dir", str(out_dir), "sync"])
    capsys.readouterr()
    return central, out_dir


@pytest.fixture
def bare(tmp_path):
    bare = tmp_path / "remote.git"
    _run(["git", "init", "--bare", str(bare)], tmp_path)
    return bare


@pytest.fixture(autouse=True)
def git_identity(monkeypatch):
    for var, val in [("GIT_AUTHOR_NAME", "T"), ("GIT_AUTHOR_EMAIL", "t@e.x"),
                     ("GIT_COMMITTER_NAME", "T"), ("GIT_COMMITTER_EMAIL", "t@e.x")]:
        monkeypatch.setenv(var, val)


def _age_last_backup(hours: float) -> None:
    ts = datetime.now(timezone.utc) - timedelta(hours=hours)
    config_module.set_value("last-backup", ts.isoformat(timespec="seconds"))


def test_backup_without_target_fails_clearly(central_with_ideas, capsys):
    assert main(["backup"]) == 1
    assert "no backup target configured" in capsys.readouterr().err


def test_setup_github_inits_repo_and_pushes_immediately(central_with_ideas, bare, capsys):
    central, _ = central_with_ideas
    assert main(["backup", "setup", "--github", str(bare)]) == 0
    assert (central / ".git").is_dir()
    assert "brainny backup:" in _bare_log(bare)
    assert config_module.get_value("backup-auto") == "true"
    assert config_module.get_value("last-backup")


def test_backup_not_due_does_nothing(central_with_ideas, bare, capsys):
    main(["backup", "setup", "--github", str(bare)])
    capsys.readouterr()
    assert main(["backup"]) == 0
    assert "not due yet" in capsys.readouterr().out


def test_due_but_unchanged_does_not_push_or_reset_clock(central_with_ideas, bare, capsys):
    main(["backup", "setup", "--github", str(bare)])
    _age_last_backup(100)
    before = config_module.get_value("last-backup")
    capsys.readouterr()
    assert main(["backup"]) == 0
    assert "nothing new" in capsys.readouterr().out
    assert config_module.get_value("last-backup") == before


def test_capture_triggers_backup_once_cadence_elapsed(central_with_ideas, bare, tmp_path, capsys):
    _, out_dir = central_with_ideas
    main(["backup", "setup", "--github", str(bare)])
    commits_after_setup = _bare_log(bare).count("\n")

    # inside the 72h window: a new capture mirrors to central but doesn't push
    main(["--out-dir", str(out_dir), "capture", str(FIXTURES / "sample_entries.json"), "--project", "myproj", "--session", "s2"])
    assert _bare_log(bare).count("\n") == commits_after_setup

    # window elapsed: the next capture pushes everything pending
    _age_last_backup(73)
    main(["--out-dir", str(out_dir), "capture", str(FIXTURES / "sample_entries.json"), "--project", "myproj", "--session", "s3"])
    assert _bare_log(bare).count("\n") == commits_after_setup + 1


def test_custom_interval(central_with_ideas, bare, capsys):
    main(["backup", "setup", "--github", str(bare), "--interval-hours", "1"])
    _age_last_backup(2)
    assert config_module.get_value("backup-interval-hours") == "1"
    capsys.readouterr()
    main(["backup"])
    assert "not due" not in capsys.readouterr().out


def test_drive_mirror_copies_and_skips_when_unchanged(central_with_ideas, tmp_path, capsys):
    central, _ = central_with_ideas
    drive = tmp_path / "My Drive"
    drive.mkdir()
    assert main(["backup", "setup", "--drive", str(drive)]) == 0
    assert (drive / "brainny-central" / "myproj" / "graph.json").exists()
    capsys.readouterr()
    assert main(["backup", "--now"]) == 0
    assert "nothing new" in capsys.readouterr().out


def test_drive_setup_rejects_missing_folder(central_with_ideas, tmp_path, capsys):
    assert main(["backup", "setup", "--drive", str(tmp_path / "nope")]) == 1


def test_off_stops_auto_backup(central_with_ideas, bare, capsys):
    _, out_dir = central_with_ideas
    main(["backup", "setup", "--github", str(bare)])
    main(["backup", "off"])
    _age_last_backup(100)
    n = _bare_log(bare).count("\n")
    main(["--out-dir", str(out_dir), "capture", str(FIXTURES / "sample_entries.json"), "--project", "myproj", "--session", "s2"])
    assert _bare_log(bare).count("\n") == n


def test_status_shows_backup_line(central_with_ideas, bare, capsys):
    _, out_dir = central_with_ideas
    main(["backup", "setup", "--github", str(bare)])
    capsys.readouterr()
    main(["--out-dir", str(out_dir), "status"])
    assert "backup: github (auto, every 72h), last 0.0h ago" in capsys.readouterr().out
