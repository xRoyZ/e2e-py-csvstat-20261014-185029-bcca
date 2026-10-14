"""CLI level test for the text report.

This exercises the real ``csvstat data.csv`` path, including
``csvstat.reader.open_table``. The reader lands with ticket #1, so until it is
on main the test skips instead of asserting the temporary answer of the stub.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import write_csv

from csvstat import reader
from csvstat.cli import main
from csvstat.models import CsvStatError


def _require_reader(path: Path) -> None:
    try:
        reader.open_table(path, ",", None)
    except CsvStatError as exc:
        if "not implemented" in str(exc):
            pytest.skip("csvstat.reader lands with ticket #1")
        raise


def test_cli_prints_one_block_per_column_and_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = write_csv(
        tmp_path,
        "data.csv",
        "name,age\nann,30\nbob,40\ncara,\n",
    )
    _require_reader(path)

    code = main([str(path)])
    captured = capsys.readouterr()

    assert code == 0
    assert captured.err == ""
    assert "column: name (text)" in captured.out
    assert "column: age (numeric)" in captured.out
    assert "unique" in captured.out
    assert "min" in captured.out
    assert "max" in captured.out
    assert "mean" in captured.out
    assert "missing" in captured.out
