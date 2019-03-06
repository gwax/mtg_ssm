"""Card and set index container."""

import collections
import string
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from uuid import UUID

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.mtg import util
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet


def name_card_sort_key(card: ScryCard) -> Tuple[str, int, str]:
    """Key function for sorting cards in a by-name list."""
    card_num, card_var = util.collector_int_var(card)
    return (card.set, card_num or 0, card_var or "")  # TODO: sort by set release date


def set_card_sort_key(card: ScryCard) -> Tuple[int, str]:
    """Key function for sorting cards in a by-set list."""
    card_num, card_var = util.collector_int_var(card)
    return (card_num or 0, card_var or "")


def build_snnms(
    card: ScryCard
) -> Iterable[Tuple[str, str, Optional[str], Optional[int]]]:
    """Build set, name, number, multiverse id tuple keys."""
    mvids: List[Optional[int]] = [None]
    if card.multiverse_ids is not None:
        mvids += card.multiverse_ids
    for mvid in mvids:
        yield (card.set, card.name, card.collector_number, mvid)
        yield (card.set, card.name, None, mvid)
        for i, card_face in enumerate(card.card_faces or ()):
            yield (card.set, card_face.name, card.collector_number, mvid)
            yield (
                card.set,
                card_face.name,
                card.collector_number + string.ascii_lowercase[i],
                mvid,
            )
            yield (card.set, card_face.name, None, mvid)


class ScryfallDataIndex:
    """Card and set indexes for scryfall data."""

    def __init__(self) -> None:
        self.id_to_card: Dict[UUID, ScryCard] = {}
        self.name_to_cards: Dict[str, List[ScryCard]] = {}
        self.setcode_to_cards: Dict[str, List[ScryCard]] = {}
        self.id_to_setindex: Dict[UUID, int] = {}
        self.setcode_to_set: Dict[str, ScrySet] = {}
        self.snnm_to_id: Dict[
            Tuple[str, str, Optional[str], Optional[int]], Set[UUID]
        ] = {}

    def load_data(self, scrydata: ScryfallDataSet) -> None:
        """Load all cards and sets from a Scryfall data set."""
        self.id_to_card = {}
        self.id_to_setindex = {}
        self.setcode_to_set = {}

        self.snnm_to_id = collections.defaultdict(set)

        name_to_unsorted_cards: Dict[str, List[ScryCard]] = collections.defaultdict(
            list
        )
        setcode_to_unsorted_cards: Dict[str, List[ScryCard]] = collections.defaultdict(
            list
        )

        for card in scrydata.cards:
            self.id_to_card[card.id] = card
            name_to_unsorted_cards[card.name].append(card)
            setcode_to_unsorted_cards[card.set].append(card)
            for snnm in build_snnms(card):
                self.snnm_to_id[snnm].add(card.id)
        self.snnm_to_id = dict(self.snnm_to_id)

        for set_ in scrydata.sets:
            self.setcode_to_set[set_.code] = set_

        for cards_list in name_to_unsorted_cards.values():
            cards_list.sort(key=name_card_sort_key)
        self.name_to_cards = dict(name_to_unsorted_cards)

        for cards_list in setcode_to_unsorted_cards.values():
            cards_list.sort(key=set_card_sort_key)
            self.id_to_setindex.update({c.id: i for i, c in enumerate(cards_list)})
        self.setcode_to_cards = dict(setcode_to_unsorted_cards)


class Oracle:
    """Container for an indexed Scryfall data set."""

    def __init__(self, scrydata: ScryfallDataSet) -> None:
        self._scrydata = scrydata
        self.cards = scrydata.cards
        self.sets = scrydata.sets
        self.index = ScryfallDataIndex()
        self.index.load_data(scrydata)
