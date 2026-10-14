"""Tests for the csvstat CLI skeleton.

These cover what the skeleton itself delivers: the argument parser, the
pre-read path guard and the fact that the four feature modules exist with the
agreed signatures. They never assert the temporary answer of a module another
ticket still has to implement.
"""

from __future__ import annotations

import inspect
import subprocess
import sys
from pathlib import Path

import pytest

from csvstat import analyze as analyze_module
from csvstat import jsonreport, reader, textreport
from csvstat.cli import main

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_help_exits_zero_and_lists_file_and_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "file" in out
    assert "--delimiter" in out
    assert "--columns" in out
    assert "--json" in out


def test_missing_path_prints_one_line_and_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.csv"
    code = main([str(missing)])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("csvstat: ")


def test_directory_prints_one_line_and_exits_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 2
    assert captured.out == ""
    lines = captured.err.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("csvstat: ")


def test_feature_modules_expose_documented_signatures() -> None:
    assert list(inspect.signature(reader.open_table).parameters) == [
        "path",
        "delimiter",
        "columns",
    ]
    assert list(inspect.signature(analyze_module.analyze).parameters) == [
        "source",
        "column_names",
        "rows",
    ]
    assert list(inspect.signature(textreport.format_text).parameters) == ["report"]
    assert list(inspect.signature(jsonreport.format_json).parameters) == ["report"]


def test_module_help_exits_zero() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "csvstat", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--delimiter" in result.stdout
    assert "--columns" in result.stdout
    assert "--json" in result.stdout


def test_module_missing_path_exits_two(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    result = subprocess.run(
        [sys.executable, "-m", "csvstat", str(missing)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr.startswith("csvstat: ")
    assert len(result.stderr.splitlines()) == 1
