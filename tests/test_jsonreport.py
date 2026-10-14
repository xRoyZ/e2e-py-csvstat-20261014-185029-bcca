"""Tests for the JSON rendering of a report (``csvstat.jsonreport``).

These build :class:`Report` fixtures directly, so they do not depend on the
reader or the analyzer implemented by other tickets. They pin the documented
JSON shape, the JSON number types, the column order and the correct escaping
of file content (quotes, backslashes and newlines) through :func:`json.loads`.
"""

from __future__ import annotations

import json

from csvstat.jsonreport import format_json
from csvstat.models import ColumnStats, Report


def _numeric(name: str) -> ColumnStats:
    return ColumnStats(
        name=name,
        kind="numeric",
        count=3,
        missing=1,
        unique=None,
        minimum=1.0,
        maximum=9.5,
        mean=4.25,
    )


def _text(name: str) -> ColumnStats:
    return ColumnStats(
        name=name,
        kind="text",
        count=4,
        missing=2,
        unique=3,
        minimum=None,
        maximum=None,
        mean=None,
    )


def test_numeric_and_text_shape() -> None:
    report = Report(file="data.csv", rows=4, columns=[_numeric("age"), _text("city")])

    parsed = json.loads(format_json(report))

    assert parsed == {
        "file": "data.csv",
        "rows": 4,
        "columns": {
            "age": {
                "type": "numeric",
                "count": 3,
                "min": 1.0,
                "max": 9.5,
                "mean": 4.25,
                "missing": 1,
            },
            "city": {
                "type": "text",
                "unique": 3,
                "missing": 2,
            },
        },
    }


def test_text_column_has_no_numeric_fields() -> None:
    report = Report(file="data.csv", rows=4, columns=[_text("city")])

    entry = json.loads(format_json(report))["columns"]["city"]

    assert entry["type"] == "text"
    assert "min" not in entry
    assert "max" not in entry
    assert "mean" not in entry
    assert "count" not in entry


def test_every_figure_is_a_json_number_not_a_string() -> None:
    report = Report(file="data.csv", rows=4, columns=[_numeric("age"), _text("city")])

    parsed = json.loads(format_json(report))
    numeric = parsed["columns"]["age"]
    text = parsed["columns"]["city"]

    for value in (
        parsed["rows"],
        numeric["count"],
        numeric["missing"],
        text["unique"],
        text["missing"],
    ):
        assert isinstance(value, int)
        assert not isinstance(value, str)
    for value in (numeric["min"], numeric["max"], numeric["mean"]):
        assert isinstance(value, float)
        assert not isinstance(value, str)


def test_column_order_follows_report_columns() -> None:
    report = Report(
        file="data.csv",
        rows=0,
        columns=[_text("beta"), _numeric("alpha"), _text("gamma")],
    )

    parsed = json.loads(format_json(report))

    assert list(parsed["columns"]) == ["beta", "alpha", "gamma"]


def test_file_content_with_quotes_backslashes_and_newlines_round_trips() -> None:
    tricky_name = 'we"ird\\name\nline\t"end\\'
    tricky_file = 'C:\\dir\\"sub"\nfile, name.csv'
    report = Report(file=tricky_file, rows=1, columns=[_numeric(tricky_name)])

    parsed = json.loads(format_json(report))

    assert parsed["file"] == tricky_file
    assert tricky_name in parsed["columns"]


def test_output_is_exactly_one_json_object() -> None:
    report = Report(file="data.csv", rows=1, columns=[_numeric("n")])

    output = format_json(report)

    assert output.count("\n") == 0
    assert json.loads(output)["file"] == "data.csv"
