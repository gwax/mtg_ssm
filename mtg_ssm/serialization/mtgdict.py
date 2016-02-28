"""Methods for managing data in the form of dicts."""

from mtg_ssm.mtg import models


def get_printing(coll, card_dict):
    """Given a card dict and various indexes, get the matching CardPrinting."""
    mtgjsid = card_dict.get('id')
    set_code = card_dict.get('set')
    name = card_dict.get('name')
    mvid = card_dict.get('multiverseid')
    number = card_dict.get('number')

    if mtgjsid is not None and mtgjsid in coll.id_to_printing:
        return coll.id_to_printing[mtgjsid]

    print('Could not find card by id, trying (set, name, num, mvid).')
    set_name_num_mv = (set_code, name, number, mvid)
    if set_name_num_mv in coll.set_name_num_mv_to_printings:
        prints = coll.set_name_num_mv_to_printings[set_name_num_mv]
        if len(prints) == 1:
            return prints[0]

    print('trying (set, name, mv)')
    set_name_mv = (set_code, name, mvid)
    if set_name_mv in coll.set_name_mv_to_printings:
        prints = coll.set_name_mv_to_printings[set_name_mv]
        if len(prints) == 1:
            return prints[0]

    print('trying (set, name, number)')
    set_name_num = (set_code, name, number)
    if set_name_num in coll.set_name_num_to_printings:
        prints = coll.set_name_num_to_printings[set_name_num]
        if len(prints) == 1:
            return prints[0]

    print('trying (set, name)')
    set_and_name = (set_code, name)
    if set_and_name in coll.set_and_name_to_printings:
        prints = coll.set_and_name_to_printings[set_and_name]
        if len(prints) == 1:
            return prints[0]

    print('Warning: Could not find printing for {}'.format(card_dict))
    return None


def load_counts(collection, card_dicts):
    """Load counts from dicts of card info/counts into a Collection."""
    for card_dict in card_dicts:
        printing = get_printing(collection, card_dict)

        for counttype in models.CountTypes:
            count = card_dict.get(counttype.name)
            if count is not None:
                existing = printing.counts.setdefault(counttype, 0)
                printing.counts[counttype] = existing + count
