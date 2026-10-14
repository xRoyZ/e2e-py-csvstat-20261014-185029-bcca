"""JSON rendering of a report."""

from __future__ import annotations

from csvstat.models import CsvStatError, Report


def format_json(report: Report) -> str:
    """Render ``report`` as exactly one JSON object.

    Implemented by ticket #2 ("Add the JSON output mode").
    """
    raise CsvStatError("jsonreport is not implemented yet")
