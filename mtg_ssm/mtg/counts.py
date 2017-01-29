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
from typing import Mapping

NAME_SUBSTITUTIONS = [
    ('Ae', 'Æ'),
    ('Jo', 'Jö'),
]
NAME_SUBSTITUTIONS += [(right, left) for (left, right) in NAME_SUBSTITUTIONS]


class Error(Exception):
    """Base exception for this module."""


class UnknownPrintingError(Error):
    """Raised when a printing cannot be found in count conversions."""


class CountTypes(enum.Enum):
    """Enum for possible card printing types (normal, foil)."""
    copies = 'copies'
    foils = 'foils'


def new_print_counts() -> Mapping[str, Mapping[CountTypes, int]]:
    """Get an appropriate defaultdict set up for use ase print counts."""
    return collections.defaultdict(collections.Counter)


def find_printing(cdb, set_code, name, set_number, multiverseid, strict=True):
    """Attempt to find a CardPrinting from given parameters."""
    print('Searching => Set: %s; Name: %s; Number: %s, Multiverse ID: %s' % (
        set_code, name, set_number, multiverseid))
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
    printing = None
    for snnm_key in snnm_keys:
        found_printings = cdb.set_name_num_mv_to_printings.get(snnm_key, [])
        if len(found_printings) == 1:
            printing = found_printings[0]
            break
        elif found_printings and not strict:
            found_printings = sorted(found_printings, key=lambda p: p.id_)
            printing = found_printings[0]
            break
    if printing is not None:
        print('Found => Set: %s; Name: %s; Number: %s; Multiverse ID: %s' % (
            printing.set_code, printing.card_name, printing.set_number,
            printing.multiverseid))
    return printing


def coerce_card_row(card_count):
    """Given a card_row dict, coerce types to match desired input."""
    int_keys = ['multiverseid'] + [ct.name for ct in CountTypes]
    for key in int_keys:
        try:
            card_count[key] = int(card_count[key])
        except (KeyError, TypeError, ValueError):
            pass
    return card_count


def aggregate_print_counts(cdb, card_rows, strict):
    """Given a card database Iterable[card_row], return print_counts"""
    print_counts = new_print_counts()
    for card_row in card_rows:
        if not any(card_row.get(ct.name) for ct in CountTypes):
            continue
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
                print_counts[printing.id_][count_type] += count
    return print_counts


def merge_print_counts(*print_counts_args):
    """Merge two sets of print_counts."""
    merged_counts = new_print_counts()
    for print_counts in print_counts_args:
        for print_id, counts in print_counts.items():
            merged_counts[print_id].update(counts)
    return merged_counts


def diff_print_counts(left, right):
    """Subtract right print counts from left print counts."""
    print_counts = new_print_counts()
    for print_id in left.keys() | right.keys():
        left_counts = left.get(print_id, {})
        right_counts = right.get(print_id, {})
        for key in left_counts.keys() | right_counts.keys():
            value = left_counts.get(key, 0) - right_counts.get(key, 0)
            if value:
                print_counts[print_id][key] = value
    return print_counts
