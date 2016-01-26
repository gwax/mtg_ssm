"""Methods for managing data in the form of dicts."""

import collections

from mtg_ssm.db import models


def get_printing(
        card_dict, id_to_print, set_name_num_mv_to_prints,
        set_name_mv_to_prints, set_name_num_to_prints):
    """Given a card dict and various indexes, get the matching CardPrinting."""
    mtgjsid = card_dict.get('id')
    set_code = card_dict.get('set')
    name = card_dict.get('name')
    mvid = card_dict.get('multiverseid')
    number = card_dict.get('number')

    if mtgjsid is not None and mtgjsid in id_to_print:
        return id_to_print[mtgjsid]

    if set_code is None or name is None:
        print('Card has no set or card has no name and cannot be found.')
        return None

    print('Could not find card by id, trying (set, name, num, mvid).')
    set_name_num_mv = (set_code, name, number, mvid)
    if set_name_num_mv in set_name_num_mv_to_prints:
        prints = set_name_num_mv_to_prints[set_name_num_mv]
        if len(prints) == 1:
            return prints[0]
        else:
            print('{} entries found.'.format(len(prints)))

    print('trying (set, name, mv)')
    set_name_mv = (set_code, name, mvid)
    if set_name_mv in set_name_mv_to_prints:
        prints = set_name_mv_to_prints[set_name_mv]
        if len(prints) == 1:
            return prints[0]
        else:
            print('{} entries found.'.format(len(prints)))

    print('trying (set, name, number)')
    set_name_num = (set_code, name, number)
    if set_name_num in set_name_num_to_prints:
        prints = set_name_num_to_prints[set_name_num]
        if len(prints) == 1:
            return prints[0]
        else:
            print('{} entries found.'.format(len(prints)))

    print('Warning: Could not find printing for {}'.format(card_dict))
    return None


def load_counts(session, card_dicts):
    """Load counts from dicts of card info/counts into the database."""
    printings = session.query(models.CardPrinting)
    id_to_print = {}
    set_name_num_mv_to_prints = collections.defaultdict(list)
    set_name_mv_to_prints = collections.defaultdict(list)
    set_name_num_to_prints = collections.defaultdict(list)
    for printing in printings:
        set_code = printing.set_code
        name = printing.card_name
        mvid = printing.multiverseid
        num = printing.set_number
        id_to_print[printing.id] = printing
        set_name_num_mv_to_prints[(set_code, name, num, mvid)].append(printing)
        set_name_mv_to_prints[(set_code, name, mvid)].append(printing)
        set_name_num_to_prints[(set_code, name, num)].append(printing)

    for card_dict in card_dicts:
        printing = get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        for key in models.CountTypes.__members__.keys():
            count = card_dict.get(key)
            if count is not None:
                printing.counts[key] = count
            elif printing is not None and key in printing.counts:
                del printing.counts[key]
