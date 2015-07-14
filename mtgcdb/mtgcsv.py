"""Code for handling data from csv files."""

import sqlalchemy.orm as sqlo

from mtgcdb import models

def header():
    return [
        'set',
        'name',
        'number',
        'multiverseid',
    ]

def get_rows(session):
    card_sets = session.query(models.CardSet) \
        .options(sqlo.subqueryload('printings').joinedload('card')) \
        .order_by(models.CardSet.release_date) \
        .all()
    for card_set in card_sets:
        for printing in card_set.printings:
            yield {
                'set': card_set.code, 'name': printing.card.name,
                'number': printing.set_number,
                'multiverseid': printing.multiverseid,
            }
