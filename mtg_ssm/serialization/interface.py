"""Interface definition for serializers."""

import abc
import collections
from typing import Dict

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import models


class Error(Exception):
    """Base error for serializers."""


class InvalidExtensionOrFormat(Error):
    """Raised if an invalid extension or format is provided."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


def find_printing(cdb, set_code, name, set_number, multiverseid, strict=True):
    """Attempt to find a CardPrinting from given parameters."""
    name = name or ''
    names = [name]
    if 'Ae' in name:
        names.append(name.replace('Ae', 'Æ'))
    if 'Jo' in name:
        names.append(name.replace('Jo', 'Jö'))
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


def coerce_count(card_count):
    """Given a counts dict, coerce types to match desired input."""
    if 'multiverseid' in card_count:
        try:
            card_count['multiverseid'] = int(card_count['multiverseid'])
        except (TypeError, ValueError):
            pass
    for counttype in models.CountTypes:
        countname = counttype.name
        if countname in card_count:
            try:
                card_count[countname] = int(card_count[countname])
            except (TypeError, ValueError):
                pass
    return card_count


def build_print_counts(cdb, card_counts, strict=True):
    """Given a card database and card_counts, return print counts"""
    print_counts = collections.defaultdict(
        lambda: collections.defaultdict(int))
    for card_count in card_counts:
        card_count = coerce_count(card_count)
        printing_id = card_count.get('id')
        printing = cdb.id_to_printing.get(printing_id)
        if printing is None:
            print('id not found for printing, searching')
            printing = find_printing(
                cdb=cdb,
                set_code=card_count.get('set'),
                name=card_count.get('name'),
                set_number=card_count.get('number'),
                multiverseid=card_count.get('multiverseid'),
                strict=strict)
        if printing is None:
            raise DeserializationError(
                'Could not match id to known printing from counts: %r' %
                card_count)
        for count_type in models.CountTypes:
            count_name = count_type.name
            count = card_count.get(count_name)
            if count:
                print_counts[printing][count_type] += count
    return print_counts


def merge_print_counts(*print_counts_args):
    """Merge two sets of print_counts."""
    print_counts = collections.defaultdict(
        lambda: collections.defaultdict(int))
    for in_print_counts in print_counts_args:
        for printing, counts in in_print_counts.items():
            for key, value in counts.items():
                print_counts[printing][key] += value
    return print_counts


class MtgSsmSerializer(metaclass=abc.ABCMeta):
    """Abstract interface for a mtg ssm serializer."""

    format = None  # type: str
    extension = None  # type: str

    _format_to_serializer = None
    _extension_to_serializer = None

    def __init__(self, cdb: card_db.CardDb) -> None:
        self.cdb = cdb

    @abc.abstractmethod
    def write(self, filename: str, print_counts) -> None:
        """Write print counts to a file."""

    @abc.abstractmethod
    def read(self, filename: str) -> Dict[
            models.CardPrinting, Dict[models.CountTypes, int]]:
        """Read print counts from file."""

    @classmethod
    def _register_subclasses(cls):
        """Register formats and extensions for all subclasses."""
        cls._format_to_serializer = {}
        cls._extension_to_serializer = {}
        subclasses = collections.deque(cls.__subclasses__())
        while subclasses:
            subclass = subclasses.popleft()
            if subclass.format is not None:
                cls._format_to_serializer[subclass.format] = subclass
            if subclass.extension is not None:
                cls._extension_to_serializer[subclass.extension] = subclass
            subclasses.extend(subclass.__subclasses__())

    @classmethod
    def all_formats(cls):
        """List of all valid serializer formats."""
        if cls._format_to_serializer is None:
            cls._register_subclasses()
        formats = ['auto']
        formats.extend(cls._format_to_serializer)
        return formats

    @classmethod
    def by_extension_and_format(cls, extension: str, ser_format: str):
        """Get the appropriate serialzer for a file."""
        if cls._format_to_serializer is None:
            cls._register_subclasses()
        if ser_format == 'auto':
            serializer = cls._extension_to_serializer.get(extension.lstrip('.'))
        else:
            serializer = cls._format_to_serializer.get(ser_format)

        if serializer is None:
            raise InvalidExtensionOrFormat(
                'Cannot find serializer for format: %s and extension %s' % (
                    ser_format, extension))
        return serializer
