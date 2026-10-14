"""Human readable, plain text rendering of a report."""

from __future__ import annotations

from csvstat.models import CsvStatError, Report


def format_text(report: Report) -> str:
    """Render ``report`` as plain text.

    Implemented by ticket #3 ("Compute column statistics and render the text
    report").
    """
    raise CsvStatError("textreport is not implemented yet")
