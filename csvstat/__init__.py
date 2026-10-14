"""csvstat — a small command line tool for per-column statistics over CSV files.

Only the standard library is used at runtime. The command line entry point is
:func:`csvstat.cli.main`; every failure is reported as a single line on stderr
prefixed with ``csvstat: `` and exits with code 2.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
