"""Data bundle definitions."""

import copy
from collections import Counter
from typing import NamedTuple

from mtg_ssm.scryfall.models import ScryCard, ScryCardLayout, ScryMigration, ScrySet, ScrySetType


class ScryfallDataSet(NamedTuple):
    """Bundle for storing Scryfall data."""

    sets: list[ScrySet]
    cards: list[ScryCard]
    migrations: list[ScryMigration]


def recount_sets(sets: list[ScrySet], cards: list[ScryCard]) -> list[ScrySet]:
    """Return sets with card counts updated to match the provided card list."""
    set_code_to_count = Counter(card.set for card in cards)
    recounted_sets = []
    for set_ in sets:
        card_count = set_code_to_count[set_.code]
        if set_.card_count == card_count:
            recounted_sets.append(set_)
            continue
        recounted_set = copy.copy(set_)
        recounted_set.card_count = card_count
        recounted_sets.append(recounted_set)
    return recounted_sets


def filter_cards_and_sets(  # noqa: C901
    scryfall_data: ScryfallDataSet,
    *,
    exclude_set_types: set[ScrySetType] | None = None,
    exclude_card_layouts: set[ScryCardLayout] | None = None,
    exclude_digital: bool = False,
    exclude_foreing_only: bool = False,
    merge_promos: bool = False,
) -> ScryfallDataSet:
    """Filter a ScryfallDataSet to exclude desired set types, card layouts, and digital only products."""
    accepted_setcodes = set()
    remapped_setcodes = {}
    for set_ in scryfall_data.sets:
        if exclude_set_types and set_.set_type in exclude_set_types:
            continue
        if exclude_digital and set_.digital:
            continue
        if (
            merge_promos
            and set_.set_type == ScrySetType.PROMO
            and set_.parent_set_code is not None
            and set_.code == f"p{set_.parent_set_code}"
        ):
            remapped_setcodes[set_.code] = set_.parent_set_code
            continue
        accepted_setcodes.add(set_.code)

    accepted_cards = []
    nonempty_setcodes = set()
    for card_loop in scryfall_data.cards:
        card = card_loop  # capture loop variable
        while card.set in remapped_setcodes:
            collector_number = card.collector_number
            if collector_number.isdigit():
                collector_number += "p"
            card = copy.copy(card)
            card.set = remapped_setcodes[card.set]
            card.collector_number = collector_number
        if card.set not in accepted_setcodes:
            continue
        if exclude_card_layouts and card.layout in exclude_card_layouts:
            continue
        if exclude_digital and card.digital:
            continue
        if exclude_foreing_only and card.lang != "en":
            continue
        accepted_cards.append(card)
        nonempty_setcodes.add(card.set)

    accepted_sets = [
        s
        for s in scryfall_data.sets
        if s.code in accepted_setcodes and s.code in nonempty_setcodes
    ]
    accepted_sets = recount_sets(accepted_sets, accepted_cards)

    return ScryfallDataSet(
        sets=accepted_sets,
        cards=accepted_cards,
        migrations=scryfall_data.migrations,
    )
