"""CLI entry points added in OPERATIONS.md §6 steps 1-4: the banner, bare
`brainny` invocation, `--version`, the status/config/search/recent/open
commands, and config set-central / sync.
"""

from pathlib import Path

import pytest

import brainny.config as config_module
from brainny.banner import render_banner
from brainny.capture import capture
from brainny.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_bare_invocation_shows_banner_and_exits_zero(capsys):
    code = main([])
    assert code == 0
    out = capsys.readouterr().out
    assert "brAInny" in out
    assert "Run `brainny --help`" in out


def test_version_flag_prints_version_and_exits(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert out.strip().startswith("brainny ")


def test_help_flag_includes_banner(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "brAInny" in out
    assert "usage: brainny" in out


def test_render_banner_plain_when_no_color(monkeypatch):
    monkeypatch.setattr("brainny.banner._color_enabled", lambda: False)
    out = render_banner()
    assert "\033[" not in out
    assert "brAInny" in out


def test_render_banner_colored(monkeypatch):
    monkeypatch.setattr("brainny.banner._color_enabled", lambda: True)
    out = render_banner()
    assert "\033[" in out
    # still recoverable as plain text once ANSI codes are stripped
    import re

    plain = re.sub(r"\033\[[0-9;]*m", "", out)
    assert "brAInny" in plain


# ---- step 2: status / config / search / recent / open ----


@pytest.fixture
def isolated_config(tmp_path, monkeypatch):
    """Never let CLI tests touch the real ~/.brainny/config.json."""
    config_dir = tmp_path / "home-brainny"
    monkeypatch.setattr(config_module, "DEFAULT_CONFIG_DIR", config_dir)
    return config_dir


def test_status_on_empty_graph(tmp_path, capsys):
    code = main(["--out-dir", str(tmp_path / "out"), "status"])
    assert code == 0
    out = capsys.readouterr().out
    assert "ideas: 0" in out


def test_status_reports_counts_and_domains(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)

    code = main(["--out-dir", str(out_dir), "status"])
    assert code == 0
    out = capsys.readouterr().out
    assert "ideas: 2" in out
    assert "domains: 1" in out
    assert "central folder: not configured" in out


def test_status_shows_configured_central_folder(tmp_path, capsys, isolated_config):
    main(["config", "set", "central-folder", "/some/path"])
    capsys.readouterr()

    code = main(["--out-dir", str(tmp_path / "out"), "status"])
    assert code == 0
    out = capsys.readouterr().out
    assert "central folder: /some/path" in out


def test_config_set_then_get_one_key(capsys, isolated_config):
    assert main(["config", "set", "project-nature", "a tool"]) == 0
    capsys.readouterr()
    assert main(["config", "get", "project-nature"]) == 0
    assert capsys.readouterr().out.strip() == "a tool"


def test_config_get_missing_key_fails(capsys, isolated_config):
    code = main(["config", "get", "nope"])
    assert code == 1
    assert "not set" in capsys.readouterr().err


def test_config_get_all_lists_everything(capsys, isolated_config):
    main(["config", "set", "a", "1"])
    capsys.readouterr()
    main(["config", "set", "b", "2"])
    capsys.readouterr()

    assert main(["config", "get"]) == 0
    out = capsys.readouterr().out
    assert "a = 1" in out
    assert "b = 2" in out


def test_config_get_empty_lists_known_keys(capsys, isolated_config):
    assert main(["config", "get"]) == 0
    out = capsys.readouterr().out
    assert "central-folder" in out


def test_search_finds_by_tag_and_domain(tmp_path, capsys):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)

    assert main(["--out-dir", str(out_dir), "search", "dedup"]) == 0
    out = capsys.readouterr().out
    assert "1 match" in out
    assert "Never let a similarity threshold" in out


def test_search_no_match(tmp_path, capsys):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)

    assert main(["--out-dir", str(out_dir), "search", "zzz-nope"]) == 0
    assert "no matches" in capsys.readouterr().out


def test_recent_respects_day_window(tmp_path, capsys):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)

    assert main(["--out-dir", str(out_dir), "recent", "--days", "7"]) == 0
    assert "2 idea(s)" in capsys.readouterr().out

    assert main(["--out-dir", str(out_dir), "recent", "--days", "0"]) == 0
    assert "nothing captured" in capsys.readouterr().out


def test_open_fails_cleanly_when_no_html(tmp_path, capsys):
    code = main(["--out-dir", str(tmp_path / "out"), "open"])
    assert code == 1
    assert "doesn't exist yet" in capsys.readouterr().err


def test_open_launches_browser(tmp_path, capsys, monkeypatch):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)
    from brainny.graph import load_graph
    from brainny.viz import save_html

    save_html(load_graph(out_dir), out_dir)

    opened = {}
    monkeypatch.setattr("webbrowser.open", lambda url: opened.setdefault("url", url))

    code = main(["--out-dir", str(out_dir), "open"])
    assert code == 0
    assert opened["url"].startswith("file:")
    assert "opened" in capsys.readouterr().out


# ---- step 4: config set-central / sync ----


def test_set_central_creates_missing_directory(tmp_path, capsys, isolated_config):
    target = tmp_path / "does" / "not" / "exist" / "yet"
    assert not target.exists()

    code = main(["config", "set-central", str(target)])
    assert code == 0
    assert target.is_dir()
    assert config_module.get_value("central-folder") == str(target)
    assert "central folder set to" in capsys.readouterr().out


def test_set_central_rejects_a_file_path(tmp_path, capsys, isolated_config):
    target = tmp_path / "a-file.txt"
    target.write_text("x")

    code = main(["config", "set-central", str(target)])
    assert code == 1
    assert "not a directory" in capsys.readouterr().err


def test_sync_without_central_configured_fails(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="p", session="s1", out_dir=out_dir)

    code = main(["--out-dir", str(out_dir), "sync"])
    assert code == 1
    assert "no central folder configured" in capsys.readouterr().err


def test_sync_with_no_local_ideas_fails(tmp_path, capsys, isolated_config):
    main(["config", "set-central", str(tmp_path / "central")])
    capsys.readouterr()

    code = main(["--out-dir", str(tmp_path / "out"), "sync"])
    assert code == 1
    assert "nothing to sync" in capsys.readouterr().err


def test_sync_pushes_graph_and_html_to_inferred_project_dir(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)

    central = tmp_path / "central"
    main(["config", "set-central", str(central)])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync"])
    assert code == 0
    out = capsys.readouterr().out
    assert "synced 2 idea(s)" in out

    assert (central / "myproj" / "graph.json").exists()
    assert (central / "myproj" / "graph.html").exists()


def test_sync_project_flag_overrides_inference(tmp_path, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)

    central = tmp_path / "central"
    main(["config", "set-central", str(central)])

    main(["--out-dir", str(out_dir), "sync", "--project", "other-name"])
    assert (central / "other-name" / "graph.json").exists()
    assert not (central / "myproj" / "graph.json").exists()


def test_status_reports_sync_drift(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    central = tmp_path / "central"
    main(["config", "set-central", str(central)])
    main(["--out-dir", str(out_dir), "sync"])
    capsys.readouterr()

    # drift: capture one more idea locally without re-syncing
    extra = tmp_path / "extra.json"
    extra.write_text(
        '[{"kind": "insight", "title": "t3", "summary": "s3", "domain": "d"}]', encoding="utf-8"
    )
    capture(extra, project="myproj", session="s2", out_dir=out_dir)
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "status"])
    assert code == 0
    out = capsys.readouterr().out
    assert "+1 idea(s) since last sync" in out


def test_status_shows_in_sync_after_sync(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    central = tmp_path / "central"
    main(["config", "set-central", str(central)])
    main(["--out-dir", str(out_dir), "sync"])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "status"])
    assert code == 0
    assert "(in sync)" in capsys.readouterr().out


# ---- step 5: GitHub sync (--push) ----
# Real git repos in tmp_path, not mocks — a bare repo stands in for
# "GitHub", matching how this project tests everything else for real.


def _run(cmd, cwd):
    import subprocess

    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)


@pytest.fixture
def git_central(tmp_path):
    """A central folder that's already a git repo with a remote (a local
    bare repo standing in for GitHub) — the state brainny expects to find,
    since it never runs `git init`/`git remote add` itself."""
    bare = tmp_path / "remote.git"
    central = tmp_path / "central"
    _run(["git", "init", "--bare", str(bare)], tmp_path)
    _run(["git", "init", str(central)], tmp_path)
    _run(["git", "-C", str(central), "checkout", "-B", "main"], tmp_path)
    _run(["git", "-C", str(central), "config", "user.email", "test@example.com"], tmp_path)
    _run(["git", "-C", str(central), "config", "user.name", "Test"], tmp_path)
    _run(["git", "-C", str(central), "remote", "add", "origin", str(bare)], tmp_path)
    (central / ".gitkeep").write_text("", encoding="utf-8")
    _run(["git", "-C", str(central), "add", "."], tmp_path)
    _run(["git", "-C", str(central), "commit", "-m", "init"], tmp_path)
    # local branch is explicitly "main" so a plain later `git push` (what
    # _maybe_push does) tracks origin/main unambiguously
    _run(["git", "-C", str(central), "push", "-u", "origin", "main"], tmp_path)
    return central, bare


def _bare_log(bare: Path) -> str:
    return _run(["git", "log", "--oneline", "--all"], bare).stdout


def test_sync_no_push_flag_does_not_touch_git(tmp_path, capsys, isolated_config, git_central):
    central, bare = git_central
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync"])
    assert code == 0
    out = capsys.readouterr().out
    assert "rerun with `brainny sync --push`" in out
    assert "myproj" not in _bare_log(bare)


def test_sync_push_commits_and_pushes(tmp_path, capsys, isolated_config, git_central):
    central, bare = git_central
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync", "--push"])
    assert code == 0
    out = capsys.readouterr().out
    assert "pushed to" in out
    assert "brainny sync: myproj (2 idea(s))" in _bare_log(bare)


def test_sync_push_second_run_with_no_changes_is_a_noop(tmp_path, capsys, isolated_config, git_central):
    central, bare = git_central
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    main(["--out-dir", str(out_dir), "sync", "--push"])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync", "--push"])
    assert code == 0
    assert "nothing new to push" in capsys.readouterr().out


def test_sync_git_auto_push_config_skips_flag(tmp_path, capsys, isolated_config, git_central):
    central, bare = git_central
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    main(["config", "set", "git-auto-push", "true"])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync"])
    assert code == 0
    assert "pushed to" in capsys.readouterr().out
    assert "myproj" in _bare_log(bare)


def test_sync_push_without_git_repo_fails_clearly(tmp_path, capsys, isolated_config):
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(tmp_path / "plain-central")])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync", "--push"])
    assert code == 1
    assert "is not a git repo" in capsys.readouterr().err


def test_sync_push_without_remote_fails_clearly(tmp_path, capsys, isolated_config):
    central = tmp_path / "central"
    _run(["git", "init", str(central)], tmp_path)
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync", "--push"])
    assert code == 1
    assert "no git remote" in capsys.readouterr().err


def test_sync_no_remote_no_push_is_informational_only(tmp_path, capsys, isolated_config):
    central = tmp_path / "central"
    _run(["git", "init", str(central)], tmp_path)
    out_dir = tmp_path / "out"
    capture(FIXTURES / "sample_entries.json", project="myproj", session="s1", out_dir=out_dir)
    main(["config", "set-central", str(central)])
    capsys.readouterr()

    code = main(["--out-dir", str(out_dir), "sync"])
    assert code == 0
    assert "local sync only" in capsys.readouterr().out


# --- regression: version resolution must survive namespace-package shadowing ---

def test_get_version_is_nonempty():
    from brainny._version import get_version

    v = get_version()
    assert isinstance(v, str) and v and v != "0.0.0"


def test_python_m_runs_from_parent_of_clone():
    """`python -m brainny.cli --version` and `python -m brainny --version` must
    not crash when the working directory contains a folder named `brainny`
    (repo-root shadowing makes `import brainny` a namespace package with no
    `__version__`). Regression for the ImportError on cli.py's version import.
    """
    import subprocess
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    parent = repo_root.parent  # contains the clone dir, itself named "brainny"
    for target in ("brainny.cli", "brainny"):
        r = subprocess.run(
            [sys.executable, "-m", target, "--version"],
            cwd=parent,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 0, f"{target}: {r.stderr or r.stdout}"
        assert "brainny" in (r.stdout + r.stderr).lower()
