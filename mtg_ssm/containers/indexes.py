"""Card and set index container."""

import collections
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from uuid import UUID

from mtg_ssm.mtg import util
from mtg_ssm.scryfall.fetcher import ScryfallData
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet


def name_card_sort_key(card: ScryCard) -> Tuple[str, int, str, Tuple[int, ...], UUID]:
    """Key function for sorting cards in a by-name list."""
    card_num, card_var = util.collector_int_var(card)
    return (
        card.set,
        card_num or 0,
        card_var or "",
        tuple(card.multiverse_ids or (0,)),
        card.id,
    )


def set_card_sort_key(card: ScryCard) -> Tuple[int, str, Tuple[int, ...], str, UUID]:
    """Key function for sorting cards in a by-set list."""
    card_num, card_var = util.collector_int_var(card)
    return (
        card_num or 0,
        card_var or "",
        tuple(card.multiverse_ids or (0,)),
        card.name,
        card.id,
    )


class ScryfallDataIndex:
    """Card and set indexes for scryfall data."""

    def __init__(self) -> None:
        self.id_to_card: Dict[UUID, ScryCard] = {}
        self.name_to_cards: Dict[str, List[ScryCard]] = {}
        self.setcode_to_cards: Dict[str, List[ScryCard]] = {}
        self.setcode_to_id_to_index: Dict[str, Dict[UUID, int]] = {}
        self.setcode_to_set: Dict[str, ScrySet] = {}

    def load_data(self, scrydata: ScryfallData) -> None:
        """Load all cards and sets from a Scryfall data set."""
        self.id_to_card = {}
        self.name_to_cards = {}
        self.setcode_to_cards = {}
        self.setcode_to_id_to_index = {}
        self.setcode_to_set = {}

        name_to_unsorted_cards: Dict[str, Set[ScryCard]] = collections.defaultdict(set)
        setcode_to_unsorted_cards: Dict[str, Set[ScryCard]] = collections.defaultdict(
            set
        )

        for card in scrydata.cards:
            self.id_to_card[card.id] = card
            name_to_unsorted_cards[card.name].add(card)
            setcode_to_unsorted_cards[card.set].add(card)
        for set_ in scrydata.sets:
            self.setcode_to_set[set_.code] = set_

        for name, unsorted_cards in name_to_unsorted_cards.items():
            self.name_to_cards[name] = sorted(unsorted_cards, key=name_card_sort_key)

        for setcode, unsorted_cards in setcode_to_unsorted_cards.items():
            sorted_cards = sorted(unsorted_cards, key=set_card_sort_key)
            self.setcode_to_cards[setcode] = sorted_cards
            self.setcode_to_id_to_index[setcode] = {
                c.id: i for i, c in enumerate(sorted_cards)
            }
