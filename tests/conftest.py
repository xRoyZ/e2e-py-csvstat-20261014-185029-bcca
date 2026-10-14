"""Shared test helpers for the csvstat test suite."""

from __future__ import annotations

from pathlib import Path


def write_csv(tmp_path: Path, name: str, content: str) -> Path:
    """Write a UTF-8 fixture CSV file and return its path."""
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path
