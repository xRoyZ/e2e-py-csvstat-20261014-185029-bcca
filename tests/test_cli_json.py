"""CLI-level tests for ``csvstat --json``.

The test drives :func:`csvstat.cli.main` over a real fixture file and the real
reader and analyzer from this sprint, then asserts that stdout parses to the
documented JSON object. The reader and the analyzer are implemented by two
sibling tickets of this sprint; until those land the pipeline is still a stub,
so the end-to-end test is skipped rather than asserting the temporary answer of
a module nobody has written yet.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from csvstat import analyze as analyze_module
from csvstat import jsonreport, reader
from csvstat.cli import main
from csvstat.models import ColumnStats, CsvStatError, Report
from tests.conftest import write_csv


def _pipeline_is_implemented(tmp_path: Path) -> bool:
    """Return whether the reader and the analyzer already deliver a report."""
    probe = write_csv(tmp_path, "probe.csv", "n\n1\n2\n")
    try:
        column_names, rows = reader.open_table(probe, ",", None)
        report = analyze_module.analyze(str(probe), column_names, rows)
    except CsvStatError:
        return False
    return report.rows == 2


def test_json_output_parses_to_documented_object(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    if not _pipeline_is_implemented(tmp_path):
        pytest.skip("reader/analyzer are implemented by sibling tickets #1 and #3")

    path = write_csv(
        tmp_path,
        "people.csv",
        "name,age\nalice,30\nbob,\ncarol,25\n",
    )

    code = main(["--json", str(path)])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    parsed = json.loads(captured.out)
    assert parsed == {
        "file": str(path),
        "rows": 3,
        "columns": {
            "name": {"type": "text", "unique": 3, "missing": 0},
            "age": {
                "type": "numeric",
                "count": 2,
                "min": 25.0,
                "max": 30.0,
                "mean": 27.5,
                "missing": 1,
            },
        },
    }


def test_json_flag_writes_exactly_the_formatter_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = write_csv(tmp_path, "any.csv", "age\n1\n")
    report = Report(
        file=str(path),
        rows=3,
        columns=[
            ColumnStats(
                name="age",
                kind="numeric",
                count=2,
                missing=1,
                unique=None,
                minimum=1.0,
                maximum=2.0,
                mean=1.5,
            )
        ],
    )
    monkeypatch.setattr(reader, "open_table", lambda *a, **k: (["age"], iter([["1"]])))
    monkeypatch.setattr(analyze_module, "analyze", lambda *a, **k: report)

    code = main(["--json", str(path)])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    assert captured.out == jsonreport.format_json(report) + "\n"


def test_json_respects_delimiter_and_column_order(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    if not _pipeline_is_implemented(tmp_path):
        pytest.skip("reader/analyzer are implemented by sibling tickets #1 and #3")

    path = write_csv(
        tmp_path,
        "scores.csv",
        "a;b;c\n1;x;10\n2;y;20\n",
    )

    code = main(["--json", "--delimiter", ";", "--columns", "c,a", str(path)])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""
    parsed = json.loads(captured.out)
    assert list(parsed["columns"]) == ["c", "a"]
    assert parsed["columns"]["c"]["type"] == "numeric"
    assert parsed["columns"]["a"]["type"] == "numeric"
