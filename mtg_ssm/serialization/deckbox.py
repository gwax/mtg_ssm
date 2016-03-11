"""CSV Serializer for Deckbox import/export."""

import csv

from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface


DECKBOX_EDITION_TO_RANGE_AND_SETNAMES = {
    'Champs': [(None, None, 'Champs and States')],
    'Commander 2013': [(None, None, 'Commander 2013 Edition')],
    'Commander': [(None, None, 'Magic: The Gathering-Commander')],
    'Conspiracy': [(None, None, 'Magic: The Gathering—Conspiracy')],
    'From the Vault: Annihilation': [
        (None, None, 'From the Vault: Annihilation (2014)')],
    'Introductory Two-Player Set': [(None, None, 'Rivals Quick Start Set')],
    'Magic 2015 Clash Pack Promos': [(None, None, 'Clash Pack')],
    'Magic Game Day Cards': [(None, None, 'Magic Game Day')],
    'Multiverse Gift Box Cards': [(None, None, 'Multiverse Gift Box')],
    'Planechase 2012': [(None, None, 'Planechase 2012 Edition')],
    'Portal Demogame': [(None, None, 'Portal Demo Game')],
    'WotC Online Store': [(None, None, 'Wizards of the Coast Online Store')],
    'WPN/Gateway': [
        (1, 20, 'Gateway'),
        (21, 100, 'Wizards Play Network'),
    ],
}
MTGJSON_TO_DECKBOX_SETNAME = {
    s: k
    for k, v in DECKBOX_EDITION_TO_RANGE_AND_SETNAMES.items()
    for _, _, s in v
}

DECKBOX_HEADER = [
    'Count',
    'Tradelist Count',
    'Name',
    'Edition',
    'Card Number',
    'Condition',
    'Language',
    'Foil',
    'Signed',
    'Artist Proof',
    'Altered Art',
    'Misprint',
    'Promo',
    'Textless',
    'My Price',
]


def get_deckbox_name(card):
    """Given a card, return an appropriate name for deckbox, or None."""
    if card.name != card.names[0]:
        return None

    if card.layout == 'split':
        cardname = ' // '.join(card.names)
    else:
        cardname = card.name

    cardname = cardname.replace('Æ', 'Ae')
    return cardname


def rows_from_printing(printing):
    """Given a CardPrinting yield rows for copies and foils, if present."""
    name = get_deckbox_name(printing.card)
    set_name = printing.set.name
    edition = MTGJSON_TO_DECKBOX_SETNAME.get(set_name, set_name)
    row_base = {
        'Tradelist Count': 0,
        'Edition': edition,
        'Card Number': printing.set_integer,
        'Condition': 'Near Mint',
        'Language': 'English',
        'Signed': None,
        'Artist Proof': None,
        'Altered Art': None,
        'Misprint': None,
        'Promo': 'promo' if printing.set.type_ == 'promo' else None,
        'Textless': None,
        'My Price': None,
    }
    if name is not None:
        row_base['Name'] = name
        copies = printing.counts.get(models.CountTypes.copies, 0)
        foils = printing.counts.get(models.CountTypes.foils, 0)
        if copies:
            # yield {**row_base, 'Foil': None, 'Count': copies}
            copies_row = row_base.copy()
            copies_row.update({'Foil': None, 'Count': copies})
            yield copies_row
        if foils:
            # yield {**row_base, 'Foil': 'foil', 'Count': foils}
            foils_row = row_base.copy()
            foils_row.update({'Foil': 'foil', 'Count': foils})
            yield foils_row


def deckbox_rows_from_collection(coll):
    """Generator that yields csv rows from a collection."""
    for card_set in coll.card_sets:
        for printing in card_set.printings:
            yield from rows_from_printing(printing)


def get_mtgj_setname(edition, number):
    """Use the remappings to get the setname from a deckbox edition."""
    if edition not in DECKBOX_EDITION_TO_RANGE_AND_SETNAMES:
        return edition

    for start, end, setname in DECKBOX_EDITION_TO_RANGE_AND_SETNAMES[edition]:
        if ((start is None or int(number) >= start) and
                (end is None or int(number) <= end)):
            return setname


def create_counts_row(coll, deckbox_row):
    """Given a row from a deckbox csv file, return a counts row."""
    edition = deckbox_row['Edition']
    number = deckbox_row['Card Number']
    mtgj_setname = get_mtgj_setname(edition, number)
    set_code = coll.setname_to_card_set[mtgj_setname].code
    counts = int(deckbox_row['Count']) + int(deckbox_row['Tradelist Count'])
    countname = 'foils' if deckbox_row['Foil'] == 'foil' else 'copies'
    return {
        'name': deckbox_row['Name'].split('//')[0].strip(),
        'set': set_code,
        'number': number,
        countname: counts,
    }


class MtgDeckboxSerializer(interface.MtgSsmSerializer):
    """MtgSsmSerializer for reading/writing deckbox compatible csv files."""

    format = 'deckbox'
    extension = None

    def write_to_file(self, filename: str) -> None:
        """Write the collection to a deckbox csv file."""
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, DECKBOX_HEADER)
            writer.writeheader()
            for row in deckbox_rows_from_collection(self.collection):
                writer.writerow(row)

    def read_from_file(self, filename: str) -> None:
        """Read collection counts from deckbox csv file."""
        with open(filename, 'r') as deckbox_file:
            reader = csv.DictReader(deckbox_file)
            for row in reader:
                self.load_counts(
                    create_counts_row(self.collection, row),
                    strict=False)
