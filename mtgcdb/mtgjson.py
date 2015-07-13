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
        card_set = update_set(session, set_data)
        for card_data in set_data['cards']:
            card = update_card(session, card_data)
            session.flush()  # Make sure card.id and card_set.id exist
            update_printing(session, card_data, card, card_set)


def update_set(session, set_data):
    """Update sets in database from mtgjson set data."""
    card_set = find_or_create(session, models.CardSet, code=set_data['code'])
    card_set.name = set_data['name']
    card_set.release_date = datetime.datetime.strptime(
        set_data['releaseDate'], '%Y-%m-%d').date()
    card_set.type = set_data['type']
    card_set.online_only = set_data.get('onlineOnly', False)

    if 'block' in set_data:
        card_block = find_or_create(
            session, models.CardBlock, name=set_data['block'])
        card_set.block = card_block
    else:
        card_set.block = None

    return card_set


def update_card(session, card_data):
    """Update a card from mtgjson data."""
    card = find_or_create(session, models.Card, name=card_data['name'])
    card.types = set(
        find_or_create(session, models.CardType, name=card_type)
        for card_type in card_data.get('types', []))
    card.supertypes = set(
        find_or_create(session, models.CardSupertype, name=card_supertype)
        for card_supertype in card_data.get('supertypes', []))
    return card


def update_printing(session, card_data, card, card_set):
    """Update a card printing."""
    printing = find_or_create(
        session, models.CardPrinting, _card_id=card.id, _set_id=card_set.id,
        set_number=card_data.get('number'),
        multiverseid=card_data.get('multiverseid'))

    printing.artist = find_or_create(
        session, models.Artist, name=card_data['artist'])
    return printing
