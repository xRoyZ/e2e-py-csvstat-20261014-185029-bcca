"""Helpers kept for data written by the older import format."""

import ast


def parse_legacy(text):
    """Parse a legacy value written as a Python literal.

    Only literals are accepted; ``ast.literal_eval`` refuses anything that
    would need code to be executed.
    """
    return ast.literal_eval("(" + text + ")")


def read_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None
