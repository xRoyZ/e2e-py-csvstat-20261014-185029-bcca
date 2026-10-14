"""Tests for :func:`csvstat.textreport.format_text`."""

from __future__ import annotations

from csvstat.models import ColumnStats, Report
from csvstat.textreport import format_text


def _numeric(
    name: str = "value",
    count: int = 3,
    missing: int = 0,
    minimum: float | None = 1.0,
    maximum: float | None = 3.5,
    mean: float | None = 2.0,
) -> ColumnStats:
    return ColumnStats(
        name=name,
        kind="numeric",
        count=count,
        missing=missing,
        unique=None,
        minimum=minimum,
        maximum=maximum,
        mean=mean,
    )


def _text(name: str = "color", count: int = 4, missing: int = 1) -> ColumnStats:
    return ColumnStats(
        name=name,
        kind="text",
        count=count,
        missing=missing,
        unique=2,
        minimum=None,
        maximum=None,
        mean=None,
    )


def test_numeric_block_shows_name_type_and_all_figures() -> None:
    report = Report(file="data.csv", rows=3, columns=[_numeric()])
    text = format_text(report)
    assert "column: value (numeric)" in text
    for label in ("count", "min", "max", "mean", "missing"):
        assert label in text
    assert "1" in text
    assert "3.5" in text


def test_text_block_shows_unique_and_missing() -> None:
    report = Report(file="data.csv", rows=5, columns=[_text()])
    text = format_text(report)
    assert "column: color (text)" in text
    assert "unique" in text
    assert "missing" in text


def test_mean_is_rounded_to_four_decimals() -> None:
    report = Report(file="data.csv", rows=3, columns=[_numeric(mean=1 / 3)])
    text = format_text(report)
    assert "0.3333" in text


def test_whole_number_mean_keeps_four_decimals() -> None:
    report = Report(file="data.csv", rows=3, columns=[_numeric(mean=2.0)])
    assert "2.0000" in format_text(report)


def test_numeric_column_without_values_does_not_crash() -> None:
    column = _numeric(count=0, missing=2, minimum=None, maximum=None, mean=None)
    text = format_text(Report(file="data.csv", rows=2, columns=[column]))
    assert "column: value (numeric)" in text
    assert "n/a" in text


def test_layout_is_aligned() -> None:
    report = Report(file="data.csv", rows=3, columns=[_numeric()])
    text = format_text(report)
    stat_lines = [line for line in text.splitlines() if line.startswith("  ")]
    assert stat_lines
    for line in stat_lines:
        assert line.startswith("  ")
        assert len(line) > 10
        assert line[9] == " "
    assert "  count   " in text
    assert "  missing " in text


def test_control_characters_in_column_names_are_neutralised() -> None:
    raw_name = "weird\x1b[31m\r\nname"
    column = _numeric(name=raw_name)
    text = format_text(Report(file="data.csv", rows=1, columns=[column]))
    assert "weird\\x1b[31m\\x0d\\x0aname (numeric)" in text
    assert "\x1b" not in text
    assert "\r" not in text


def test_file_name_is_shown() -> None:
    text = format_text(Report(file="data.csv", rows=3, columns=[_numeric()]))
    assert "data.csv" in text
    assert "rows: 3" in text
