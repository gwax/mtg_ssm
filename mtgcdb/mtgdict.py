"""Methods for managing data in the form of dicts."""

from mtgcdb import models


def find_printing(session, card_dict):
    """Given a card_dict, find the matching CardPrinting."""
    mtgj_id = card_dict.get('id')
    card_name = card_dict.get('name')
    set_code = card_dict.get('set')
    set_number = card_dict.get('number')
    multiverseid = card_dict.get('multiverseid')

    mquery = session.query(models.CardPrinting)

    if mtgj_id is not None:
        return mquery.get(mtgj_id)

    if card_name is None or set_code is None:
        return None
    mquery = mquery.filter_by(card_name=card_name, set_code=set_code)

    if set_number is not None:
        mquery = mquery.filter_by(set_number=set_number)

    if multiverseid is not None:
        mquery = mquery.filter_by(multiverseid=multiverseid)

    printings = mquery.all()
    if not printings:
        return None
    elif len(printings) > 1:
        print('Multiple matches found.')
        return None
    else:
        return printings[0]


def load_counts(session, card_dicts):
    """Load counts from dicts of card info/counts into the database."""
    for card_dict in card_dicts:
        printing = find_printing(session, card_dict)
        if printing is None:
            print('Warning: Could not find printing for {}'.format(card_dict))

        for key in models.CountTypes.__members__.keys():
            count = card_dict.get(key)
            if count is not None:
                printing.counts[key] = count
            elif printing is not None and key in printing.counts:
                del printing.counts[key]
