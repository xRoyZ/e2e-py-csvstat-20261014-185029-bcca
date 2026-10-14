"""Shared data types for csvstat.

These definitions are the single source of truth for every module of the
package: the reader, the analyzer, the text report and the JSON report all
speak in terms of :class:`CsvStatError`, :class:`ColumnStats` and
:class:`Report`.
"""

from __future__ import annotations

from dataclasses import dataclass


class CsvStatError(Exception):
    """A user-facing error.

    ``str(the_error)`` is the one-line message shown to the user. The CLI adds
    the ``csvstat: `` prefix and turns it into exit code 2; no traceback is
    ever shown.
    """


@dataclass(frozen=True)
class ColumnStats:
    """Statistics for a single column.

    ``kind`` is either ``"numeric"`` or ``"text"``. ``count`` is the number of
    parsed values for a numeric column and the number of non-empty values for a
    text column. ``missing`` counts empty or whitespace-only cells. ``unique``
    is only set for text columns, ``minimum``/``maximum``/``mean`` only for
    numeric ones; ``mean`` is unrounded.
    """

    name: str
    kind: str
    count: int
    missing: int
    unique: int | None
    minimum: float | None
    maximum: float | None
    mean: float | None


@dataclass(frozen=True)
class Report:
    """The result of analyzing one table.

    ``rows`` is the number of data rows without the header. ``columns`` are the
    per-column results in output order.
    """

    file: str
    rows: int
    columns: list[ColumnStats]
