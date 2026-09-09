"""Resolve the brAInny version even when the package is imported as a PEP 420
namespace package.

That happens whenever the repository *root* lands on ``sys.path`` — most
commonly ``python -m brainny.cli`` (or ``python -m brainny``) launched from the
*parent* directory of a clone whose folder is named ``brainny``. Python then
treats the repo root as a namespace portion and never executes
``brainny/__init__.py``, so ``brainny.__version__`` simply does not exist and
``from brainny import __version__`` raises
``ImportError: cannot import name '__version__' from 'brainny'``.

Submodule imports (``brainny._version``, ``brainny.config``, ``brainny.banner``,
…) keep working in that state, so this helper lives in its own module and is
used by ``cli.py`` / ``banner.py`` instead of ``from brainny import __version__``.
``get_version()`` never raises.
"""

from __future__ import annotations

# Keep in sync with brainny/__init__.py and pyproject.toml.
_FALLBACK_VERSION = "0.1.0"


def get_version() -> str:
    """Best-effort brAInny version string. Never raises."""
    # 1) Normal case: __init__.py executed and defined __version__.
    try:
        from brainny import __version__

        if __version__:
            return str(__version__)
    except Exception:
        pass

    # 2) Installed distribution metadata (works for editable + regular installs).
    try:
        from importlib.metadata import PackageNotFoundError, version

        try:
            return version("brainny")
        except PackageNotFoundError:
            pass
    except Exception:
        pass

    # 3) Last resort.
    return _FALLBACK_VERSION
