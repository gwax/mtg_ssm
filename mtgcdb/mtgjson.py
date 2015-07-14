"""Code for handling data from mtgjson."""

import datetime

from mtgcdb import models


def update_models(session, mtg_data):
    """Update database with data from mtgjson (assumes models exist).

    Arguments:
        session: Session, sqlalchemy session to read/write database.
        mtg_data: dict, data from json.load(s) on mtgjson data.
    """
    for set_data in mtg_data.values():
        card_set = update_set(session, set_data)
        session.flush()  # Flush to ensure card_set has an id
        set_id = card_set.id
        for card_data in set_data['cards']:
            update_card(session, card_data, set_id)


def update_set(session, set_data):
    """Update sets in database from mtgjson set data."""
    card_set = session.query(
        models.CardSet).filter_by(code=set_data['code']).first()
    if card_set is None:
        card_set = models.CardSet(code=set_data['code'])
    session.add(card_set)

    card_set.name = set_data['name']
    card_set.block = set_data.get('block')
    card_set.release_date = datetime.datetime.strptime(
        set_data['releaseDate'], '%Y-%m-%d').date()
    card_set.type = set_data['type']
    card_set.online_only = set_data.get('onlineOnly', False)
    return card_set


def update_card(session, card_data, set_id):
    """Update a card from mtgjson data."""
    card = session.query(models.Card).filter_by(
        set_id=set_id, name=card_data['name'],
        set_number=card_data.get('number'),
        multiverseid=card_data.get('multiverseid')).first()
    if card is None:
        card = models.Card(
            set_id=set_id, name=card_data['name'],
            set_number=card_data.get('number'),
            multiverseid=card_data.get('multiverseid'))
    session.add(card)

    card.artist = card_data['artist']
    return card
