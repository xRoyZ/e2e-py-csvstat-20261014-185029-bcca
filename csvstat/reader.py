"""CSV reading with delimiter, column selection and input validation."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from csvstat.models import CsvStatError


def open_table(
    path: Path,
    delimiter: str,
    columns: list[str] | None,
) -> tuple[list[str], Iterator[list[str]]]:
    """Return the output column names and a lazy iterator over the rows.

    Implemented by ticket #1 ("Implement CSV reading with delimiter, column
    selection and input errors").
    """
    raise CsvStatError("reader is not implemented yet")
