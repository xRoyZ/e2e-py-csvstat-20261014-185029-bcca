"""Column statistics over rows produced by the reader."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from csvstat.models import CsvStatError, Report


def analyze(
    source: str,
    column_names: Sequence[str],
    rows: Iterable[Sequence[str]],
) -> Report:
    """Compute per-column statistics and build a report.

    Implemented by ticket #3 ("Compute column statistics and render the text
    report").
    """
    raise CsvStatError("analyze is not implemented yet")
