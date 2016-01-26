"""Code for handling data from csv files."""

import sqlalchemy.orm as sqlo

from mtg_ssm.db import models
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
    headers.extend(models.CountTypes.__members__.keys())
    return headers


def dump_rows(session):
    """Yield mtgcsv row dicts from the database."""
    card_sets = session.query(models.CardSet) \
        .options(sqlo.joinedload('printings'))
    for card_set in card_sets:
        for printing in card_set.printings:
            card_info = {
                'set': card_set.code, 'name': printing.card.name,
                'number': printing.set_number,
                'multiverseid': printing.multiverseid,
                'mtgjid': printing.id,
            }
            card_info.update(printing.counts)
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
    for countype in models.CountTypes.__members__.keys():
        if countype in row_dict:
            card_dict[countype] = int_or_none(row_dict[countype])
    return card_dict


def read_row_counts(session, row_dicts):
    """Read mtgcsv row dicts and load counts into the database."""
    card_dicts = (process_row_dict(row_dict) for row_dict in row_dicts)
    mtgdict.load_counts(session, card_dicts)
