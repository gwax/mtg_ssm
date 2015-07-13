"""Code for handling data from mtgjson."""

import datetime

from mtgcdb import models


def find_or_create(session, model, **query):
    """Find or create a model instance using filter parameters."""
    obj = session.query(model).filter_by(**query).first()
    if obj is None:
        obj = model(**query)
        session.add(obj)
    return obj


def update_models(session, mtg_data):
    """Update database with data from mtgjson (assumes models exist).

    Arguments:
        session: Session, sqlalchemy session to read/write database.
        mtg_data: dict, data from json.load(s) on mtgjson data.
    """
    for set_data in mtg_data.values():
        update_set(session, set_data)
        for card_data in set_data['cards']:
            update_card(session, card_data, set_data['code'])


def update_set(session, set_data):
    """Update sets in database from mtgjson set data."""
    card_set = find_or_create(session, models.CardSet, code=set_data['code'])
    card_set.name = set_data['name']
    card_set.block = set_data.get('block')
    card_set.release_date = datetime.datetime.strptime(
        set_data['releaseDate'], '%Y-%m-%d').date()
    card_set.type = set_data['type']
    card_set.online_only = set_data.get('onlineOnly', False)
    return card_set


def update_card(session, card_data, set_code):
    """Update a card from mtgjson data."""
    card = find_or_create(
        session, models.Card, name=card_data['name'], set_code=set_code,
        set_number=card_data.get('number'),
        multiverseid=card_data.get('multiverseid'))
    card.artist = card_data['artist']
    return card
