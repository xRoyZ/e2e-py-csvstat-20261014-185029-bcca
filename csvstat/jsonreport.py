"""JSON rendering of a report.

The whole report is serialised with :func:`json.dumps` in one call. Column
names (and every other piece of file content that reaches this module) are
therefore escaped by the JSON encoder itself; no manual string concatenation
and no template formatting is used anywhere in this module.
"""

from __future__ import annotations

import json

from csvstat.models import ColumnStats, Report


def _numeric_entry(column: ColumnStats) -> dict[str, object]:
    """Build the JSON object for a numeric column."""
    return {
        "type": "numeric",
        "count": column.count,
        "min": column.minimum,
        "max": column.maximum,
        "mean": column.mean,
        "missing": column.missing,
    }


def _text_entry(column: ColumnStats) -> dict[str, object]:
    """Build the JSON object for a text column."""
    return {
        "type": "text",
        "unique": column.unique,
        "missing": column.missing,
    }


def format_json(report: Report) -> str:
    """Render ``report`` as exactly one JSON object.

    The object has the shape::

        {"file": ..., "rows": ...,
         "columns": {"<name>": {"type": "numeric", "count": ..., "min": ...,
                                "max": ..., "mean": ..., "missing": ...},
                     "<name>": {"type": "text", "unique": ..., "missing": ...}}}

    Columns appear in the order of ``report.columns`` and every figure is a
    JSON number (never a string).
    """
    columns: dict[str, dict[str, object]] = {}
    for column in report.columns:
        if column.kind == "numeric":
            columns[column.name] = _numeric_entry(column)
        else:
            columns[column.name] = _text_entry(column)

    payload = {
        "file": report.file,
        "rows": report.rows,
        "columns": columns,
    }
    return json.dumps(payload)
