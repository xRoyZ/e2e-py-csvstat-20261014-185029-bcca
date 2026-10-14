"""Command line entry point of csvstat.

This module is written once by the skeleton and is not edited by later tickets.
It parses the arguments, guards the input path before anything is read, wires
the reader, the analyzer and the two formatters together and renders every
:class:`CsvStatError` as a single line on stderr with exit code 2.

The values taken from the command line (``--delimiter``, ``--columns`` and the
file path) are treated as plain data only: they are never passed to ``eval``,
``exec`` or to ``str.format`` / ``%`` formatting.
"""

from __future__ import annotations

import argparse
import os
import sys

from csvstat import analyze as analyze_module
from csvstat import jsonreport, reader, textreport
from csvstat.models import CsvStatError

EXIT_OK = 0
EXIT_FAILURE = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csvstat",
        description="Print per-column statistics for a CSV file with a header row.",
    )
    parser.add_argument(
        "file",
        help="path to the CSV file to analyze",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        metavar="CHAR",
        help="field delimiter; the two characters \\t mean a tab (default: ,)",
    )
    parser.add_argument(
        "--columns",
        default=None,
        metavar="NAME[,NAME...]",
        help="comma separated list of columns to report, in this order",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="write the report as a single JSON object instead of text",
    )
    return parser


def _guard_path(path: str) -> None:
    """Refuse anything that is not a readable regular file, before reading it."""
    if not os.path.exists(path):
        raise CsvStatError(f"no such file: {path}")
    if not os.path.isfile(path):
        raise CsvStatError(f"not a regular file: {path}")
    if not os.access(path, os.R_OK):
        raise CsvStatError(f"cannot read file: {path}")


def _normalize_delimiter(value: str) -> str:
    """Turn the literal two-character sequence ``\\t`` into a real tab."""
    if value == "\\t":
        return "\t"
    return value


def main(argv: list[str] | None = None) -> int:
    """Run the csvstat CLI and return the process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    delimiter = _normalize_delimiter(args.delimiter)
    columns = args.columns.split(",") if args.columns is not None else None

    try:
        _guard_path(args.file)
        column_names, rows = reader.open_table(args.file, delimiter, columns)
        report = analyze_module.analyze(args.file, column_names, rows)
        output = jsonreport.format_json(report) if args.json else textreport.format_text(report)
    except CsvStatError as exc:
        print(f"csvstat: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    print(output)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
