"""Column statistics over rows produced by the reader.

The row iterator is consumed exactly once: every cell is folded into a small
per-column accumulator, so memory stays bounded by the running aggregates plus
the set of distinct non-empty values per column, never by the file size.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from csvstat.models import ColumnStats, Report


@dataclass
class _Accumulator:
    """Running per-column state built up during the single streaming pass."""

    name: str
    missing: int = 0
    non_empty: int = 0
    total: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    numeric: bool = True
    distinct: set[str] = field(default_factory=set)


MISSING_MARKER = ""


def _parse_number(text: str) -> float | None:
    """Return ``text`` as a float when it is a finite number, else ``None``.

    Both integer and floating point spellings parse; a value that is not a
    finite number (``nan``, ``inf`` and friends) is treated as text because it
    cannot take part in a meaningful min/max/mean aggregate.
    """
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value):
        return None
    return value


def analyze(
    source: str,
    column_names: Sequence[str],
    rows: Iterable[Sequence[str]],
) -> Report:
    """Compute per-column statistics and build a report."""
    accumulators = [_Accumulator(name=name) for name in column_names]
    row_count = 0

    for row in rows:
        row_count += 1
        for index, accumulator in enumerate(accumulators):
            raw = row[index] if index < len(row) else MISSING_MARKER
            cell = raw if isinstance(raw, str) else str(raw)

            if cell.strip() == "":
                accumulator.missing += 1
                continue

            accumulator.non_empty += 1
            accumulator.distinct.add(cell)

            number = _parse_number(cell)
            if number is None:
                accumulator.numeric = False
                continue

            accumulator.total += number
            if accumulator.minimum is None or number < accumulator.minimum:
                accumulator.minimum = number
            if accumulator.maximum is None or number > accumulator.maximum:
                accumulator.maximum = number

    columns = [_finish(accumulator) for accumulator in accumulators]
    return Report(file=source, rows=row_count, columns=columns)


def _finish(accumulator: _Accumulator) -> ColumnStats:
    """Turn the running state of one column into its immutable result."""
    if accumulator.numeric:
        mean: float | None = None
        if accumulator.non_empty:
            mean = accumulator.total / accumulator.non_empty
        return ColumnStats(
            name=accumulator.name,
            kind="numeric",
            count=accumulator.non_empty,
            missing=accumulator.missing,
            unique=None,
            minimum=accumulator.minimum,
            maximum=accumulator.maximum,
            mean=mean,
        )

    return ColumnStats(
        name=accumulator.name,
        kind="text",
        count=accumulator.non_empty,
        missing=accumulator.missing,
        unique=len(accumulator.distinct),
        minimum=None,
        maximum=None,
        mean=None,
    )
