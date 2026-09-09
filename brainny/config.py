"""~/.brainny/config.json — small local settings store: central folder
path, GitHub remote, sync cadence, project-nature descriptor. Just
read/write plumbing (OPERATIONS.md §6 step 2); the actual sync logic
lives in brainny/cli.py's cmd_sync (step 4, local) and _maybe_push
(step 5, GitHub).
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".brainny"


def _resolve(config_dir: Path | None) -> Path:
    # late-bound: reads the module attribute at call time, not at def
    # time, so tests can monkeypatch DEFAULT_CONFIG_DIR and have it
    # actually take effect (a `config_dir: Path = DEFAULT_CONFIG_DIR`
    # default argument would freeze the value at import time instead).
    return config_dir if config_dir is not None else DEFAULT_CONFIG_DIR


KNOWN_KEYS = {
    "central-folder": "local path (optionally a git repo) ideas sync to",
    "github-remote": "git remote URL for the central folder, if any (informational; "
    "the actual push target always comes from `git remote` in the central folder itself)",
    "git-auto-push": "'true' to let `brainny sync` push without needing --push each time",
    "sync-interval-days": "how often the ambient reconciliation runs (default 3)",
    "project-nature": "one-line descriptor for this project's capture prompt",
    "onboarding-done": "'true' once the one-time central-folder setup offer "
    "(brainny-onboarding skill) has been asked, so it never asks again "
    "regardless of the answer",
}


def config_path(config_dir: Path | None = None) -> Path:
    return _resolve(config_dir) / "config.json"


def load_config(config_dir: Path | None = None) -> dict:
    path = config_path(config_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_config(config: dict, config_dir: Path | None = None) -> Path:
    resolved = _resolve(config_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    path = config_path(resolved)
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def get_value(key: str, config_dir: Path | None = None) -> str | None:
    return load_config(config_dir).get(key)


def set_value(key: str, value: str, config_dir: Path | None = None) -> Path:
    config = load_config(config_dir)
    config[key] = value
    return save_config(config, config_dir)
