"""Code for handling data from csv files."""

import sqlalchemy.orm as sqlo

from mtgcdb import models
from mtgcdb import mtgdict


def header():
    """Get the header columns for an mtgcsv file."""
    headers = [
        'set',
        'name',
        'number',
        'multiverseid',
    ]
    headers.extend(models.CountTypes.__members__.keys())
    return headers


def dump_rows(session):
    """Yield mtgcsv row dicts from the database."""
    card_sets = session.query(models.CardSet) \
        .options(sqlo.subqueryload('printings').joinedload('card')) \
        .order_by(models.CardSet.release_date) \
        .all()
    for card_set in card_sets:
        for printing in card_set.printings:
            card_info = {
                'set': card_set.code, 'name': printing.card.name,
                'number': printing.set_number,
                'multiverseid': printing.multiverseid,
            }
            card_info.update(printing.counts)
            yield card_info


def read_row_counts(session, row_dicts):
    """Read mtgcsv row dicts and load counts into the database."""
    for row_dict in row_dicts:
        card_dict = {k: v or None for k, v in row_dict.items()}
        mtgdict.load_counts(session, card_dict)
