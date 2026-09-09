"""Support ``python -m brainny`` as an alias for the ``brainny`` console script.

Both this and ``python -m brainny.cli`` are safe to run from any working
directory — version resolution goes through ``brainny._version.get_version()``,
which tolerates brainny being imported as a namespace package.
"""

from brainny.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
