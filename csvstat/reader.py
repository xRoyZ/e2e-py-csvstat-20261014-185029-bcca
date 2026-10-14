"""CSV reading with delimiter, column selection and input validation."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path

from csvstat.models import CsvStatError


def _normalize_cell(cell: str) -> str:
    """Return ``""`` for an empty or whitespace-only cell, else the cell itself."""
    if cell.strip() == "":
        return ""
    return cell


def _cell(row: list[str], index: int) -> str:
    """Return the normalised cell at ``index``, or ``""`` for a short row."""
    if index >= len(row):
        return ""
    return _normalize_cell(row[index])


def _decode_error(path: Path) -> CsvStatError:
    return CsvStatError(f"cannot decode file as UTF-8: {path}")


def open_table(
    path: Path,
    delimiter: str,
    columns: list[str] | None,
) -> tuple[list[str], Iterator[list[str]]]:
    """Return the output column names and a lazy iterator over the rows.

    The file is opened as UTF-8 and the first line is read as the header. A
    0-byte file, a file with a header but no data rows, an unknown column name
    and a UTF-8 decode error all raise :class:`CsvStatError` before returning.
    The returned iterator streams the data rows one by one, never collecting
    them into a list; empty and whitespace-only cells come back as ``""``.
    """
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)

        try:
            header = next(reader, None)
        except UnicodeDecodeError as exc:
            raise _decode_error(path) from exc

        if not header:
            raise CsvStatError(f"empty file: {path}")

        try:
            first_row = next(reader, None)
        except UnicodeDecodeError as exc:
            raise _decode_error(path) from exc

        if first_row is None:
            raise CsvStatError(f"file has a header but no data rows: {path}")

        if columns is None:
            names = list(header)
            indices = list(range(len(header)))
        else:
            names = list(columns)
            indices = []
            for name in columns:
                try:
                    indices.append(header.index(name))
                except ValueError:
                    raise CsvStatError(f"unknown column: {name}") from None

    def _iter_rows() -> Iterator[list[str]]:
        with open(path, encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            try:
                next(reader, None)
                for row in reader:
                    yield [_cell(row, index) for index in indices]
            except UnicodeDecodeError as exc:
                raise _decode_error(path) from exc

    return names, _iter_rows()
