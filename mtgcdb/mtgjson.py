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
        for card_data in set_data['cards']:
            card = update_card(session, card_data)
            session.flush()  # Flush to ensure card and card_set have ids
            update_printing(session, card_data, card.id, card_set.id)


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


def update_card(session, card_data):
    """Update a card from mtgjson data."""
    card = session.query(models.Card).filter_by(name=card_data['name']).first()
    if card is None:
        card = models.Card(name=card_data['name'])
    session.add(card)

    return card


def update_printing(session, card_data, card_id, set_id):
    """Update a card printing from mtgjson data."""
    printing = session.query(models.CardPrinting).filter_by(
        card_id=card_id, set_id=set_id, set_number=card_data.get('number'),
        multiverseid=card_data.get('multiverseid')).first()
    if printing is None:
        printing = models.CardPrinting(
            card_id=card_id, set_id=set_id, set_number=card_data.get('number'),
            multiverseid=card_data.get('multiverseid'))
    session.add(printing)

    printing.artist = card_data['artist']
    return printing
