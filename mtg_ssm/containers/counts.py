"""Helpers for tracking collection counts."""

import collections
import enum
from typing import Any, Dict, Iterable, MutableMapping
from uuid import UUID

from mtg_ssm.containers import legacy
from mtg_ssm.containers.indexes import Oracle


class Error(Exception):
    """Base exception for this module."""


class CardNotFoundError(Error):
    """Raised when we attempt to add a card to a count but cannot find it in the oracle."""


class CountType(str, enum.Enum):
    """Enum for possible card printing types (nonfoil, foil)."""

    NONFOIL = "nonfoil"
    FOIL = "foil"


ScryfallCardCount = Dict[UUID, MutableMapping[CountType, int]]
"""Mapping from scryfall id to card printing type to count."""


def aggregate_card_counts(
    card_rows: Iterable[Dict[str, Any]], oracle: Oracle
) -> ScryfallCardCount:
    """Extract card counts from card rows."""
    card_counts: ScryfallCardCount = {}
    for card_row in card_rows:
        if "scryfall_id" not in card_row:
            card_row = legacy.coerce_row(card_row, oracle)
        if not card_row:
            continue
        scryfall_id = card_row["scryfall_id"]
        if not isinstance(scryfall_id, UUID):
            scryfall_id = UUID(scryfall_id)
        counts = card_counts.get(scryfall_id, {})
        for count_type in CountType:
            value = int(card_row.get(count_type.value) or 0)
            if value:
                counts[count_type] = value + counts.get(count_type, 0)
        if counts:
            while scryfall_id in oracle.index.migrate_old_id_to_new_id:
                scryfall_id = oracle.index.migrate_old_id_to_new_id[scryfall_id]
            if scryfall_id not in oracle.index.id_to_card:
                raise CardNotFoundError(
                    f"Found counts for card={scryfall_id} not found scryfall data"
                )
            card_counts[scryfall_id] = counts
    return card_counts


def merge_card_counts(*card_counts_args: ScryfallCardCount) -> ScryfallCardCount:
    """Merge two sets of card_counts."""
    merged_counts: ScryfallCardCount = collections.defaultdict(collections.Counter)
    for card_counts in card_counts_args:
        for card_id, counts in card_counts.items():
            merged_counts[card_id].update(counts)
    return dict(merged_counts)


def diff_card_counts(
    left: ScryfallCardCount, right: ScryfallCardCount
) -> ScryfallCardCount:
    """Subtract right print counts from left print counts."""
    diffed_counts: ScryfallCardCount = collections.defaultdict(dict)
    for card_id in left.keys() | right.keys():
        left_counts = left.get(card_id, {})
        right_counts = right.get(card_id, {})
        card_counts = {
            k: left_counts.get(k, 0) - right_counts.get(k, 0)
            for k in left_counts.keys() | right_counts.keys()
        }
        card_counts = {k: v for k, v in card_counts.items() if v}
        if card_counts:
            diffed_counts[card_id] = card_counts
    return diffed_counts
