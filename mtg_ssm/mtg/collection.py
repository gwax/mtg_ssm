"""Container for holding models."""

import collections

from mtg_ssm.mtg import models


def set_code_to_printings_key(printing):
    """Sort key function for set_code_to_printings index."""
    return (
        printing.set_integer or 0,
        str(printing.set_variant),
        printing.multiverseid or 0,
        printing.card_name,
    )


def card_name_to_printing_key(printing):
    """Sort key function for card_name_to_printings index."""
    return (
        printing.set_code,
        printing.set_integer or 0,
        str(printing.set_variant),
        printing.multiverseid or 0,
    )


class Collection:
    """Container/manager object for storing models."""

    def __init__(self, mtg_json_data=None, include_online_only=False):
        self.name_to_card = {}
        self.code_to_card_set = {}
        self.setname_to_card_set = {}
        self.id_to_printing = {}

        # Card Sets Index
        self.card_sets = None

        # Printing Indexes
        self.set_code_to_printings = None
        self.card_name_to_printings = None
        self.set_name_num_mv_to_printings = None

        if mtg_json_data is not None:
            self.load_mtg_json(mtg_json_data, include_online_only)
            self.rebuild_indexes()
            self.sort_indexes()

    def load_mtg_json(self, mtg_json_data, include_online_only=False):
        """Update the collection with data from mtg_json."""
        for set_data in mtg_json_data.values():
            card_set = models.CardSet(self, set_data)
            if not include_online_only and card_set.online_only:
                continue

            self.code_to_card_set[card_set.code] = card_set
            self.setname_to_card_set[card_set.name] = card_set

            for card_data in set_data['cards']:
                card = models.Card(self, card_data)
                self.name_to_card[card.name] = card

                printing = models.CardPrinting(self, card_set.code, card_data)
                self.id_to_printing[printing.id_] = printing

    def rebuild_indexes(self):
        """Rebuild the printing indexes."""
        self.card_sets = list(self.code_to_card_set.values())

        self.set_code_to_printings = collections.defaultdict(list)
        self.card_name_to_printings = collections.defaultdict(list)
        self.set_name_num_mv_to_printings = collections.defaultdict(list)

        for printing in self.id_to_printing.values():
            self.set_code_to_printings[printing.set_code].append(printing)
            self.card_name_to_printings[printing.card_name].append(printing)
            snnm_index_keys = {
                (printing.set_code, printing.card_name, printing.set_number,
                 printing.multiverseid),
                (printing.set_code, printing.card_name, None,
                 printing.multiverseid),
                (printing.set_code, printing.card_name, printing.set_number,
                 None),
                (printing.set_code, printing.card_name, None, None),
            }
            for key in snnm_index_keys:
                self.set_name_num_mv_to_printings[key].append(printing)

    def sort_indexes(self):
        """Sort the indexes."""
        self.card_sets.sort(key=lambda cset: cset.release_date)

        for printings in self.set_code_to_printings.values():
            printings.sort(key=set_code_to_printings_key)

        for printings in self.card_name_to_printings.values():
            printings.sort(key=card_name_to_printing_key)
