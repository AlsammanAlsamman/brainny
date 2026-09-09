"""brAInny — catches your ideas before the wind."""

# Static source of truth, kept in sync with pyproject.toml and
# brainny/_version.py::_FALLBACK_VERSION.
__version__ = "0.1.0"

# When brainny is actually installed, prefer the distribution's own version so
# a stale string here can't lie. Falls back to the static value above if the
# package isn't installed (e.g. run straight from a source checkout).
try:
    from importlib.metadata import PackageNotFoundError as _PNF, version as _dist_version

    try:
        __version__ = _dist_version("brainny")
    except _PNF:
        pass
    del _dist_version, _PNF
except Exception:  # pragma: no cover - importlib.metadata is stdlib on 3.10+
    pass
