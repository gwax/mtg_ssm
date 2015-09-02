"""Methods for managing data in the form of dicts."""

from mtgcdb import models


def load_counts(session, card_dicts):
    """Load counts from dicts of card info/counts into the database."""
    printings = session.query(models.CardPrinting)
    set_name_num_mv_to_printing = {
        (p.set.code, p.card.name, p.set_number, p.multiverseid): p
        for p in printings}
    set_name_num_to_printing = {
        (p.set.code, p.card.name, p.set_number): p for p in printings}
    set_name_mv_to_printing = {
        (p.set.code, p.card.name, p.multiverseid): p for p in printings}
    for card_dict in card_dicts:
        set_name_num_mv = tuple(
            card_dict[k] for k in ['set', 'name', 'number', 'multiverseid'])

        printing = set_name_num_mv_to_printing.get(set_name_num_mv)
        if printing is None and card_dict['number'] is not None:
            print('Count not find {} trying with set number'.format(
                set_name_num_mv))
            set_name_num = set_name_num_mv[:3]
            printing = set_name_num_to_printing.get(set_name_num)

        if printing is None and card_dict['multiverseid'] is not None:
            print('Could not find {} trying with multiverseid'.format(
                set_name_num_mv))
            set_name_mv = set_name_num_mv[:2] + set_name_num_mv[3:]
            printing = set_name_mv_to_printing.get(set_name_mv)

        if printing is None:
            print('Warning: Could not find {}'.format(set_name_num_mv))

        for key in models.CountTypes.__members__.keys():
            count = card_dict.get(key)
            if count is not None:
                printing.counts[key] = count
            elif printing is not None and key in printing.counts:
                del printing.counts[key]
