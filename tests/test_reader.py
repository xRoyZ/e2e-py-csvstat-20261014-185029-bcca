"""Tests for the CSV reader: delimiter, column selection and input errors."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from conftest import write_csv

from csvstat.models import CsvStatError
from csvstat.reader import open_table


def _drain(rows: Iterator[list[str]]) -> list[list[str]]:
    return list(rows)


def test_comma_delimiter_is_default(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name,age\nAlice,30\nBob,25\n")
    names, rows = open_table(path, ",", None)
    assert names == ["name", "age"]
    assert _drain(rows) == [["Alice", "30"], ["Bob", "25"]]


def test_semicolon_delimiter(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name;age\nAlice;30\nBob;25\n")
    names, rows = open_table(path, ";", None)
    assert names == ["name", "age"]
    assert _drain(rows) == [["Alice", "30"], ["Bob", "25"]]


def test_tab_delimiter(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name\tage\nAlice\t30\n")
    names, rows = open_table(path, "\t", None)
    assert names == ["name", "age"]
    assert _drain(rows) == [["Alice", "30"]]


def test_quoted_fields(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", 'name,note\nAlice,"hello, world"\n')
    names, rows = open_table(path, ",", None)
    assert names == ["name", "note"]
    assert _drain(rows) == [["Alice", "hello, world"]]


def test_column_subset_preserves_command_line_order(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name,age,city\nAlice,30,Berlin\n")
    names, rows = open_table(path, ",", ["city", "name"])
    assert names == ["city", "name"]
    assert _drain(rows) == [["Berlin", "Alice"]]


def test_unknown_column_names_the_column(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name,age\nAlice,30\n")
    with pytest.raises(CsvStatError) as excinfo:
        open_table(path, ",", ["nope"])
    assert "nope" in str(excinfo.value)


def test_zero_byte_file_raises(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "empty.csv", "")
    with pytest.raises(CsvStatError) as excinfo:
        open_table(path, ",", None)
    assert path.name in str(excinfo.value)


def test_header_only_file_raises(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "header.csv", "name,age\n")
    with pytest.raises(CsvStatError) as excinfo:
        open_table(path, ",", None)
    assert path.name in str(excinfo.value)


def test_utf8_decode_error_raises_and_names_path(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_bytes(b"name,age\n\xff\xfe,30\n")
    with pytest.raises(CsvStatError) as excinfo:
        open_table(path, ",", None)
    assert path.name in str(excinfo.value)


def test_whitespace_only_cells_become_empty(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name,age\n   ,30\nAlice,  \n")
    names, rows = open_table(path, ",", None)
    assert names == ["name", "age"]
    assert _drain(rows) == [["", "30"], ["Alice", ""]]


def test_rows_are_streamed_lazily(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "data.csv", "name,age\nAlice,30\nBob,25\nCara,40\n")
    names, rows = open_table(path, ",", None)
    assert names == ["name", "age"]
    assert isinstance(rows, Iterator)
    assert not isinstance(rows, list)
    assert next(rows) == ["Alice", "30"]
    assert next(rows) == ["Bob", "25"]
    assert next(rows) == ["Cara", "40"]
    with pytest.raises(StopIteration):
        next(rows)
