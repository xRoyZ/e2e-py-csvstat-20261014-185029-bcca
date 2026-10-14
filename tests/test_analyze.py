"""Tests for :func:`csvstat.analyze.analyze`."""

from __future__ import annotations

from collections.abc import Iterator, Sequence

import pytest

from csvstat.analyze import analyze


def test_int_and_float_values_are_numeric() -> None:
    report = analyze("data.csv", ["value"], [["1"], ["2.5"], ["-3"]])
    column = report.columns[0]
    assert column.kind == "numeric"
    assert column.count == 3
    assert column.missing == 0
    assert column.minimum == -3
    assert column.maximum == 2.5
    assert column.mean == pytest.approx((1 + 2.5 - 3) / 3)
    assert column.unique is None
    assert report.file == "data.csv"
    assert report.rows == 3


def test_text_column_counts_unique_non_empty_values() -> None:
    rows = [["red"], ["blue"], ["red"], [""], ["blue"]]
    column = analyze("data.csv", ["color"], rows).columns[0]
    assert column.kind == "text"
    assert column.count == 4
    assert column.unique == 2
    assert column.missing == 1
    assert column.minimum is None
    assert column.maximum is None
    assert column.mean is None


def test_missing_and_whitespace_only_cells_are_missing() -> None:
    rows = [["1"], ["   "], [""], ["3"]]
    column = analyze("data.csv", ["value"], rows).columns[0]
    assert column.kind == "numeric"
    assert column.count == 2
    assert column.missing == 2
    assert column.minimum == 1
    assert column.maximum == 3
    assert column.mean == pytest.approx(2.0)


def test_one_non_numeric_cell_makes_the_whole_column_text() -> None:
    rows = [["1"], ["oops"], ["3"]]
    column = analyze("data.csv", ["value"], rows).columns[0]
    assert column.kind == "text"
    assert column.count == 3
    assert column.unique == 3
    assert column.missing == 0
    assert column.minimum is None
    assert column.maximum is None
    assert column.mean is None


def test_all_missing_column_has_no_values() -> None:
    rows = [[""], ["   "], [""]]
    column = analyze("data.csv", ["value"], rows).columns[0]
    assert column.kind == "numeric"
    assert column.count == 0
    assert column.missing == 3
    assert column.unique is None
    assert column.minimum is None
    assert column.maximum is None
    assert column.mean is None


def test_columns_keep_the_given_order_and_short_rows_count_as_missing() -> None:
    rows = [["ann", "30", "x"], ["bob"]]
    report = analyze("data.csv", ["name", "age", "tag"], rows)
    assert [column.name for column in report.columns] == ["name", "age", "tag"]
    assert report.rows == 2
    assert report.columns[1].missing == 1
    assert report.columns[2].missing == 1


class _SinglePassRows:
    """A row source that can only be iterated once."""

    def __init__(self, rows: Sequence[Sequence[str]]) -> None:
        self._rows = rows
        self.iterations = 0

    def __iter__(self) -> Iterator[Sequence[str]]:
        self.iterations += 1
        if self.iterations > 1:
            raise AssertionError("the row iterator was consumed more than once")
        return iter(self._rows)


def test_rows_are_consumed_in_a_single_streaming_pass() -> None:
    rows = _SinglePassRows([["1"], ["2"], ["3"], ["4"]])
    report = analyze("data.csv", ["value"], rows)
    assert rows.iterations == 1
    assert report.rows == 4
    assert report.columns[0].count == 4
    assert report.columns[0].mean == pytest.approx(2.5)


def test_empty_input_yields_an_empty_report() -> None:
    report = analyze("data.csv", ["value"], [])
    assert report.rows == 0
    assert report.columns[0].count == 0
    assert report.columns[0].missing == 0
