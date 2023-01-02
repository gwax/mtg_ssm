"""Data bundle definitions."""

from typing import List, NamedTuple, Optional, Set

from mtg_ssm.scryfall.models import ScryCard, ScryCardLayout, ScrySet, ScrySetType


class ScryfallDataSet(NamedTuple):
    """Bundle for storing Scryfall data."""

    sets: List[ScrySet]
    cards: List[ScryCard]


def filter_cards_and_sets(
    scryfall_data: ScryfallDataSet,
    *,
    exclude_set_types: Optional[Set[ScrySetType]] = None,
    exclude_card_layouts: Optional[Set[ScryCardLayout]] = None,
    exclude_digital: bool = False,
    exclude_foreing_only: bool = False,
) -> ScryfallDataSet:
    """Filter a ScryfallDataSet to exclude desired set types, card layouts, and digital only products."""
    accepted_setcodes = set()
    for set_ in scryfall_data.sets:
        if exclude_set_types and set_.set_type in exclude_set_types:
            continue
        if exclude_digital and set_.digital:
            continue
        accepted_setcodes.add(set_.code)

    accepted_cards = []
    nonempty_setcodes = set()
    for card in scryfall_data.cards:
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
    return ScryfallDataSet(sets=accepted_sets, cards=accepted_cards)
