"""Methods for managing data in the form of dicts."""

from mtgcdb import models


def load_counts(session, card_dicts):
    """Load counts from dicts of card info/counts into the database."""
    printings = session.query(models.CardPrinting)
    set_name_num_mv_to_printing = {
        (p.set.code, p.card.name, p.set_number, p.multiverseid): p
        for p in printings}
    for card_dict in card_dicts:
        set_name_num_mv = tuple(
            card_dict[k] for k in ['set', 'name', 'number', 'multiverseid'])
        printing = set_name_num_mv_to_printing[set_name_num_mv]
        for key in models.CountTypes.__members__.keys():
            count = card_dict.get(key)
            if count is not None:
                printing.counts[key] = count
            elif key in printing.counts:
                del printing.counts[key]
