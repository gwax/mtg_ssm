"""Code for handling data from mtgjson."""

import datetime

from mtg_ssm.db import models


def update_models(session, mtg_data, include_online_only):
    """Update database with data from mtgjson (assumes models exist).

    Arguments:
        session: Session, sqlalchemy session to read/write database.
        mtg_data: dict, data from json.load(s) on mtgjson data.
        include_online_only: process online_only sets? if False, skip.
    """
    seen_set_codes = set()
    seen_card_names = set()
    seen_printing_ids = set()
    for set_data in mtg_data.values():
        if not include_online_only and set_data.get('onlineOnly', False):
            continue

        if set_data['code'] in seen_set_codes:
            continue

        card_set = create_set(set_data)
        session.add(card_set)
        seen_set_codes.add(card_set.code)

        for card_data in set_data['cards']:
            if card_data['name'] not in seen_card_names:
                card = create_card(card_data)
                session.add(card)
                seen_card_names.add(card.name)

            if card_data['id'] not in seen_printing_ids:
                printing = create_printing(card_data, set_data['code'])
                session.add(printing)
                seen_printing_ids.add(printing.id)


def create_set(set_data):
    """Given set data, create a CardSet."""
    card_set = models.CardSet(code=set_data['code'])
    card_set.name = set_data['name']
    card_set.block = set_data.get('block')
    card_set.release_date = datetime.datetime.strptime(
        set_data['releaseDate'], '%Y-%m-%d').date()
    card_set.type = set_data['type']
    card_set.online_only = set_data.get('onlineOnly', False)
    return card_set


def create_card(card_data):
    """Given card data, create a Card."""
    card = models.Card(name=card_data['name'])
    card.strict_basic = (card_data.get('supertypes') == ['Basic'])
    return card


def create_printing(card_data, set_code):
    """Given card data, create a CardPrinting."""
    printing = models.CardPrinting(id=card_data['id'])
    printing.card_name = card_data['name']
    printing.set_code = set_code
    printing.set_number = card_data.get('number')
    printing.multiverseid = card_data.get('multiverseid')
    printing.artist = card_data['artist']
    return printing
