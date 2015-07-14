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
    query = session.query(models.CardSet).options(sqlo.joinedload('cards'))
    query = query.order_by(models.CardSet.release_date)
    card_sets = query.all()
    for card_set in card_sets:
        for card in card_set.cards:
            yield {
                'set': card.set.code, 'name': card.name,
                'number': card.set_number, 'multiverseid': card.multiverseid,
            }
