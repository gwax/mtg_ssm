"""Data bundle definitions."""

from typing import List
from typing import NamedTuple

from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet


class ScryfallDataSet(NamedTuple):
    """Bundle for storing Scryfall data."""

    sets: List[ScrySet]
    cards: List[ScryCard]


def remove_digital(scryfall_data: ScryfallDataSet) -> ScryfallDataSet:
    """Filter a ScryfallDataSet to remove all digital only sets and cards."""
    rejected_setcodes = set()
    accepted_sets = []
    for set_ in scryfall_data.sets:
        if set_.digital:
            rejected_setcodes.add(set_.code)
        else:
            accepted_sets.append(set_)
    accepted_cards = [c for c in scryfall_data.cards if c.set not in rejected_setcodes]
    return ScryfallDataSet(sets=accepted_sets, cards=accepted_cards)
