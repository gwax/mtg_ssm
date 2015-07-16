"""Methods for managing data in the form of dicts."""

from mtgcdb import models


def load_counts(session, card_dict):
    """Load card counts from a dictionary into the database."""
    card_set = session.query(models.CardSet) \
        .filter_by(code=card_dict['set']) \
        .one()
    card = session.query(models.Card) \
        .filter_by(name=card_dict['name']) \
        .one()
    printing = session.query(models.CardPrinting) \
        .filter_by(
            card_id=card.id, set_id=card_set.id,
            set_number=card_dict['number'],
            multiverseid=card_dict['multiverseid']) \
        .one()
    for key in models.CountTypes.__members__.keys():
        count = card_dict.get(key)
        if count is not None:
            printing.counts[key] = count
        elif key in printing.counts:
            del printing.counts[key]
