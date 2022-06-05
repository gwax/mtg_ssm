"""Utility functions for working with card data."""

import functools
import string
from typing import Optional, Tuple

from mtg_ssm.scryfall.models import ScryCard

STRICT_BASICS = frozenset({"Plains", "Island", "Swamp", "Mountain", "Forest"})


@functools.lru_cache(maxsize=None)
def dig_str(collector_number: str) -> Tuple[Optional[int], Optional[str]]:
    """Split a collector number into integer portion and non-digit portion."""
    digpart = []
    strpart = []
    for char in collector_number:
        if char in string.digits:
            digpart.append(char)
        else:
            strpart.append(char)
    if not digpart:
        return (None, "".join(strpart))
    return (int("".join(digpart)), "".join(strpart) or None)


def collector_int_var(card: ScryCard) -> Tuple[Optional[int], Optional[str]]:
    """Get the integer and variant portions of a card's collector number."""
    return dig_str(card.collector_number)


def is_strict_basic(card_name: str) -> bool:
    """Is the card on of the five basic lands (not Snow or Wastes)."""
    return card_name in STRICT_BASICS
