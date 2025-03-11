"""Utility functions for working with card data."""

import functools
import re

STRICT_BASICS = frozenset({"Plains", "Island", "Swamp", "Mountain", "Forest"})

COLLECTOR_NUMBER_RE = re.compile(r"(?P<prefix>.*-|\D+)?(?P<number>\d+)?(?P<suffix>\D.*)?")


@functools.cache
def collector_number_parts(collector_number: str) -> tuple[str, int, str]:
    """Split a collector number into its parts."""
    match = COLLECTOR_NUMBER_RE.match(collector_number)
    if not match:
        return ("", 0, "")
    prefix: str = match.group("prefix") or ""
    number: int = int(match.group("number")) if match.group("number") else 0
    suffix: str = match.group("suffix") or ""
    return (prefix, number, suffix)


def is_strict_basic(card_name: str) -> bool:
    """Is the card on of the five basic lands (not Snow or Wastes)."""
    return card_name in STRICT_BASICS
