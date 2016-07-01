"""Helpers for tracking collection counts.

There are two types of dictionary used in this module: card_row, and
print_counts. These dictionaries are of the following form:

print_counts:
    used for tracking aggregate counts of cards in a collection

    signature: Dict[models.CardPrinting, Dict[CountTypes, int]]

card_row:
    used for representing a single card and any counts for it

    form: {
        'id': str, 'set': str, 'name': str, 'number': str,
        'multiverseid': str/int, CountTypes.name: str/int,
        [CountTypes.name: str/int, [...]]
    }

The helper methods in this modules are primarily concerned with converting
iterables of card_row dicts into singular print_counts dicts.
"""

import collections
import enum

NAME_SUBSTITUTIONS = [
    ('Ae', 'Æ'),
    ('Jo', 'Jö'),
]


class Error(Exception):
    """Base exception for this module."""


class UnknownPrintingError(Error):
    """Raised when a printing cannot be found in count conversions."""


class CountTypes(enum.Enum):
    """Enum for possible card printing types (normal, foil)."""
    copies = 'copies'
    foils = 'foils'


def new_print_counts():
    """Get an appropriate defaultdict set up for use ase print counts."""
    return collections.defaultdict(
        lambda: collections.defaultdict(int))


def find_printing(cdb, set_code, name, set_number, multiverseid, strict=True):
    """Attempt to find a CardPrinting from given parameters."""
    name = name or ''
    names = [name]
    for sub_from, sub_to in NAME_SUBSTITUTIONS:
        if sub_from in name:
            names.append(name.replace(sub_from, sub_to))
    snnm_keys = []
    for name_var in names:
        snnm_keys.extend([
            (set_code, name_var, set_number, multiverseid),
            (set_code, name_var, None, multiverseid),
            (set_code, name_var, set_number, None),
            (set_code, name_var, None, None),
        ])
    for snnm_key in snnm_keys:
        found_printings = cdb.set_name_num_mv_to_printings.get(snnm_key, [])
        if len(found_printings) == 1 or found_printings and not strict:
            return found_printings[0]

    return None


def coerce_card_row(card_count):
    """Given a card_row dict, coerce types to match desired input."""
    int_keys = ['multiverseid'] + [ct.name for ct in CountTypes]
    for key in int_keys:
        try:
            card_count[key] = int(card_count[key])
        except (KeyError, TypeError, ValueError):
            pass
    return card_count


def aggregate_print_counts(cdb, card_rows, strict=True):
    """Given a card database Iterable[card_row], return print_counts"""
    print_counts = collections.defaultdict(
        lambda: collections.defaultdict(int))
    for card_row in card_rows:
        card_row = coerce_card_row(card_row)
        printing_id = card_row.get('id')
        printing = cdb.id_to_printing.get(printing_id)
        if printing is None:
            print('printing not found by id, searching')
            printing = find_printing(
                cdb=cdb,
                set_code=card_row.get('set'),
                name=card_row.get('name'),
                set_number=card_row.get('number'),
                multiverseid=card_row.get('multiverseid'),
                strict=strict)
        if printing is None:
            raise UnknownPrintingError(
                'Could not match id to known printing from counts: %r' %
                card_row)
        for count_type in CountTypes:
            ct_name = count_type.name
            count = card_row.get(ct_name)
            if count:
                print_counts[printing][count_type] += count
    return print_counts


def merge_print_counts(*print_counts_args):
    """Merge two sets of print_counts."""
    print_counts = new_print_counts()
    for in_print_counts in print_counts_args:
        for printing, counts in in_print_counts.items():
            for key, value in counts.items():
                print_counts[printing][key] += value
    return print_counts


def diff_print_counts(left, right):
    """Subtract right print counts from left print counts."""
    print_counts = new_print_counts()
    for printing in left.keys() | right.keys():
        left_counts = left.get(printing, {})
        right_counts = right.get(printing, {})
        for key in left_counts.keys() | right_counts.keys():
            value = left_counts.get(key, 0) - right_counts.get(key, 0)
            if value:
                print_counts[printing][key] = value
    return print_counts
