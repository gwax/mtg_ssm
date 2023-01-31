"""Data bundle definitions."""

from typing import List, NamedTuple, Optional, Set

from mtg_ssm.scryfall.models import (
    ScryCard,
    ScryCardLayout,
    ScryMigration,
    ScrySet,
    ScrySetType,
)


class ScryfallDataSet(NamedTuple):
    """Bundle for storing Scryfall data."""

    sets: List[ScrySet]
    cards: List[ScryCard]
    migrations: List[ScryMigration]


def filter_cards_and_sets(
    scryfall_data: ScryfallDataSet,
    *,
    exclude_set_types: Optional[Set[ScrySetType]] = None,
    exclude_card_layouts: Optional[Set[ScryCardLayout]] = None,
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
    for card in scryfall_data.cards:
        while card.set in remapped_setcodes:
            collector_number = card.collector_number
            if collector_number.isdigit():
                collector_number += "p"
            card = card.copy(
                update={
                    "set": remapped_setcodes[card.set],
                    "collector_number": collector_number,
                }
            )
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

    return ScryfallDataSet(
        sets=accepted_sets,
        cards=accepted_cards,
        migrations=scryfall_data.migrations,
    )
