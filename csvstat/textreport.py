"""Human readable, plain text rendering of a report.

Every piece of text that comes from the CSV (the header cells become column
names) is neutralised before it reaches stdout: control characters are turned
into visible ``\\xNN`` escapes so that neither terminal escape sequences nor
embedded newlines from cell content can steer a terminal.

Strings here are built with f-strings and ``str.ljust`` only; file content is
never handed to ``eval``/``exec``/``str.format``/``%`` formatting.
"""

from __future__ import annotations

from csvstat.models import ColumnStats, Report

_LABEL_WIDTH = 8
_NOT_AVAILABLE = "n/a"


def _sanitize(text: str) -> str:
    """Replace C0/C1 control characters and DEL with visible escapes."""
    parts: list[str] = []
    for character in text:
        code = ord(character)
        if code < 0x20 or 0x7F <= code <= 0x9F:
            parts.append(f"\\x{code:02x}")
        else:
            parts.append(character)
    return "".join(parts)


def _format_number(value: float) -> str:
    """Render a finite float without a noisy ``.0`` for whole numbers."""
    if value.is_integer():
        return str(int(value))
    return repr(value)


def _format_mean(value: float | None) -> str:
    """Render the mean rounded to exactly four decimal places."""
    if value is None:
        return _NOT_AVAILABLE
    return f"{round(value, 4):.4f}"


def _stat_line(label: str, value: str) -> str:
    return "  " + label.ljust(_LABEL_WIDTH) + value


def _numeric_lines(report_column: ColumnStats) -> list[str]:
    minimum = (
        _NOT_AVAILABLE if report_column.minimum is None else _format_number(report_column.minimum)
    )
    maximum = (
        _NOT_AVAILABLE if report_column.maximum is None else _format_number(report_column.maximum)
    )
    return [
        _stat_line("count", str(report_column.count)),
        _stat_line("min", minimum),
        _stat_line("max", maximum),
        _stat_line("mean", _format_mean(report_column.mean)),
        _stat_line("missing", str(report_column.missing)),
    ]


def _text_lines(report_column: ColumnStats) -> list[str]:
    unique = _NOT_AVAILABLE if report_column.unique is None else str(report_column.unique)
    return [
        _stat_line("unique", unique),
        _stat_line("missing", str(report_column.missing)),
    ]


def format_text(report: Report) -> str:
    """Render ``report`` as plain text, one block per column."""
    lines: list[str] = [
        f"file: {_sanitize(report.file)}",
        f"rows: {report.rows}",
    ]

    for report_column in report.columns:
        name = _sanitize(report_column.name)
        lines.append("")
        lines.append(f"column: {name} ({report_column.kind})")
        if report_column.kind == "numeric":
            lines.extend(_numeric_lines(report_column))
        else:
            lines.extend(_text_lines(report_column))

    return "\n".join(lines)
