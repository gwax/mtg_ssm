"""Code for handling data from csv files."""

from mtg_ssm.mtg import models
from mtg_ssm.serialization import mtgdict


def header():
    """Get the header columns for an mtgcsv file."""
    headers = [
        'set',
        'name',
        'number',
        'multiverseid',
        'mtgjid',
    ]
    headers.extend(ct.name for ct in models.CountTypes)
    return headers


def dump_rows(collection):
    """Yield mtgcsv row dicts from a Collection."""
    card_sets = collection.code_to_card_set.values()
    card_sets = sorted(card_sets, key=lambda cset: cset.release_date)
    for card_set in card_sets:
        for printing in card_set.printings:
            card_info = {
                'set': card_set.code, 'name': printing.card.name,
                'number': printing.set_number,
                'multiverseid': printing.multiverseid,
                'mtgjid': printing.id_,
            }
            for counttype, count in printing.counts.items():
                if count:
                    card_info[counttype.name] = count
            yield card_info


def int_or_none(value):
    """Returns an integer for 0 or non-false values, otherwise None."""
    if value == 0:
        return 0
    elif value:
        return int(value)
    else:
        return None


def process_row_dict(row_dict):
    """Given a row_dict, produce a card_dict suitable for mtgdict."""
    card_dict = {
        'set': row_dict['set'],
        'name': row_dict['name'],
        'number': row_dict['number'] or None,
        'multiverseid': int_or_none(row_dict['multiverseid']),
        'id': row_dict.get('mtgjid'),
    }
    for counttype in models.CountTypes:
        countname = counttype.name
        if countname in row_dict:
            card_dict[countname] = int_or_none(row_dict[countname])
    return card_dict


def read_row_counts(session, row_dicts):
    """Read mtgcsv row dicts and load counts into the database."""
    card_dicts = (process_row_dict(row_dict) for row_dict in row_dicts)
    mtgdict.load_counts(session, card_dicts)
