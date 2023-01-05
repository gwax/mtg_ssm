"""Card and set index container."""

import collections
import string
from typing import Dict, Iterable, List, Optional, Set, Tuple
from uuid import UUID

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.mtg import util
from mtg_ssm.scryfall.models import ScryCard, ScryMigrationStrategy, ScrySet


def name_card_sort_key(card: ScryCard) -> Tuple[str, int, str]:
    """Key function for sorting cards in a by-name list."""
    card_num, card_var = util.collector_int_var(card)
    return (card.set, card_num or 0, card_var or "")  # TODO: sort by set release date


def set_card_sort_key(card: ScryCard) -> Tuple[int, str]:
    """Key function for sorting cards in a by-set list."""
    card_num, card_var = util.collector_int_var(card)
    return (card_num or 0, card_var or "")


def build_snnmas(
    card: ScryCard,
) -> Iterable[Tuple[Optional[str], str, Optional[str], Optional[int], Optional[str]]]:
    """Build set, name, number, multiverse id tuple keys."""
    names_cnums: Set[Tuple[str, Optional[str]]] = {(card.name, card.collector_number)}
    for i, card_face in enumerate(card.card_faces or ()):
        names_cnums |= {
            (card_face.name, card.collector_number),
            (card_face.name, card.collector_number + string.ascii_lowercase[i]),
        }
    names_cnums |= {(n, None) for n, _ in names_cnums}

    sets: Set[Optional[str]] = {card.set, None}

    mvids: Set[Optional[int]] = {None} | set(card.multiverse_ids or ())

    artists: Set[Optional[str]] = {card.artist, None}

    for name, number in names_cnums:
        for set_ in sets:
            for mvid in mvids:
                for artist in artists:
                    yield (set_, name, number, mvid, artist)


class ScryfallDataIndex:
    """Card and set indexes for scryfall data."""

    def __init__(self) -> None:
        self.id_to_card: Dict[UUID, ScryCard] = {}
        self.name_to_cards: Dict[str, List[ScryCard]] = {}
        self.setcode_to_cards: Dict[str, List[ScryCard]] = {}
        self.id_to_setindex: Dict[UUID, int] = {}
        self.setcode_to_set: Dict[str, ScrySet] = {}
        self.migrate_old_id_to_new_id: Dict[UUID, UUID] = {}
        # snnma = Set, Name, (Collector) Number, Multiverse ID, Artist
        # TODO: convert to intersecting bitmap indexes
        # TODO: do we really need artist?
        self.snnma_to_id: Dict[
            Tuple[Optional[str], str, Optional[str], Optional[int], Optional[str]],
            Set[UUID],
        ] = {}

    def load_data(self, scrydata: ScryfallDataSet) -> None:
        """Load all cards and sets from a Scryfall data set."""
        self.id_to_card = {}
        self.id_to_setindex = {}
        self.setcode_to_set = {}

        self.snnma_to_id = collections.defaultdict(set)

        name_to_unsorted_cards: Dict[str, List[ScryCard]] = collections.defaultdict(
            list
        )
        setcode_to_unsorted_cards: Dict[str, List[ScryCard]] = {}

        for set_ in scrydata.sets:
            self.setcode_to_set[set_.code] = set_
            setcode_to_unsorted_cards[set_.code] = []

        for card in scrydata.cards:
            self.id_to_card[card.id] = card
            name_to_unsorted_cards[card.name].append(card)
            setcode_to_unsorted_cards[card.set].append(card)
            if not self.setcode_to_set[card.set].digital:
                for snnma in build_snnmas(card):
                    self.snnma_to_id[snnma].add(card.id)
        self.snnma_to_id = dict(self.snnma_to_id)

        for cards_list in name_to_unsorted_cards.values():
            cards_list.sort(key=name_card_sort_key)
        self.name_to_cards = dict(name_to_unsorted_cards)

        for cards_list in setcode_to_unsorted_cards.values():
            cards_list.sort(key=set_card_sort_key)
            self.id_to_setindex.update({c.id: i for i, c in enumerate(cards_list)})
        self.setcode_to_cards = dict(setcode_to_unsorted_cards)

        for migration in scrydata.migrations:
            if (
                migration.migration_strategy == ScryMigrationStrategy.MERGE
                and migration.new_scryfall_id
            ):
                self.migrate_old_id_to_new_id[
                    migration.old_scryfall_id
                ] = migration.new_scryfall_id


class Oracle:
    """Container for an indexed Scryfall data set."""

    def __init__(self, scrydata: ScryfallDataSet) -> None:
        self._scrydata = scrydata
        self.cards = scrydata.cards
        self.sets = scrydata.sets
        self.index = ScryfallDataIndex()
        self.index.load_data(scrydata)
