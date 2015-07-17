"""Code for handling data from mtgjson."""

import datetime

from mtgcdb import models


def update_models(session, mtg_data):
    """Update database with data from mtgjson (assumes models exist).

    Arguments:
        session: Session, sqlalchemy session to read/write database.
        mtg_data: dict, data from json.load(s) on mtgjson data.
    """
    setcode_to_set = {s.code: s for s in session.query(models.CardSet)}
    cardname_to_card = {c.name: c for c in session.query(models.Card)}
    for set_data in mtg_data.values():
        update_set(session, set_data, setcode_to_set)
        for card_data in set_data['cards']:
            update_card(session, card_data, cardname_to_card)

    session.flush()
    set_card_num_mv_to_printing = {
        (p.set_id, p.card_id, p.set_number, p.multiverseid): p
        for p in session.query(models.CardPrinting)}
    for set_data in mtg_data.values():
        set_id = setcode_to_set[set_data['code']].id
        for card_data in set_data['cards']:
            card_id = cardname_to_card[card_data['name']].id
            update_printing(
                session, card_data, card_id, set_id,
                set_card_num_mv_to_printing)


def update_set(session, set_data, code_to_set):
    """Update sets in database from mtgjson set data."""
    code = set_data['code']
    if code in code_to_set:
        card_set = code_to_set[code]
    else:
        card_set = models.CardSet(code=code)
        code_to_set[code] = card_set
        session.add(card_set)
    card_set.name = set_data['name']
    card_set.block = set_data.get('block')
    card_set.release_date = datetime.datetime.strptime(
        set_data['releaseDate'], '%Y-%m-%d').date()
    card_set.type = set_data['type']
    card_set.online_only = set_data.get('onlineOnly', False)
    return card_set


def update_card(session, card_data, name_to_card):
    """Update a card from mtgjson data."""
    name = card_data['name']
    if name in name_to_card:
        card = name_to_card[name]
    else:
        card = models.Card(name=name)
        name_to_card[name] = card
        session.add(card)
    return card


def update_printing(session, card_data, card_id, set_id, scnm_to_print):
    """Update a card printing from mtgjson data."""
    setnum = card_data.get('number')
    mvid = card_data.get('multiverseid')
    scnm_key = (set_id, card_id, setnum, mvid)
    if scnm_key in scnm_to_print:
        printing = scnm_to_print[scnm_key]
    else:
        printing = models.CardPrinting(
            card_id=card_id, set_id=set_id, set_number=setnum,
            multiverseid=mvid)
        scnm_to_print[scnm_key] = printing
        session.add(printing)
    printing.artist = card_data['artist']
    return printing
