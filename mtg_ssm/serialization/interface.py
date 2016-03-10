"""Interface definition for serializers."""

import abc
import collections
from typing import Any, Dict

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models


class Error(Exception):
    """Base error for serializers."""


class InvalidExtensionOrFormat(Error):
    """Raised if an invalid extension or format is provided."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


def find_printing(coll, set_code, name, set_number, multiverseid, strict=True):
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
        found_printings = coll.set_name_num_mv_to_printings.get(snnm_key, [])
        if len(found_printings) == 1 or found_printings and not strict:
            return found_printings[0]

    return None


def coerce_counts(counts_dict):
    """Given a counts dict, coerce types to match desired input."""
    if 'multiverseid' in counts_dict:
        try:
            counts_dict['multiverseid'] = int(counts_dict['multiverseid'])
        except (TypeError, ValueError):
            pass
    for counttype in models.CountTypes:
        countname = counttype.name
        if countname in counts_dict:
            try:
                counts_dict[countname] = int(counts_dict[countname])
            except (TypeError, ValueError):
                pass
    return counts_dict


class MtgSsmSerializer(metaclass=abc.ABCMeta):
    """Abstract interface for a mtg ssm serializer."""

    _format_to_serializer = None
    _extension_to_serializer = None

    def __init__(self, coll: collection.Collection):
        self.collection = coll

    @property
    @abc.abstractmethod
    def extension(self) -> str:
        """The extension this serializer is authoritative over."""

    @property
    @abc.abstractmethod
    def format(self) -> str:
        """The format name for this serializer."""

    @abc.abstractmethod
    def write_to_file(self, filename: str) -> None:
        """Write the collection to a file."""

    @abc.abstractmethod
    def read_from_file(self, filename: str) -> None:
        """Read counts from file and add them to the collection."""

    def load_counts(self, counts: Dict[Any, Any], strict: bool=True) -> None:
        """Load counts from a dict into the collection.

        Arguments:
            counts: a dict containing key 'id' mapping to mtgjson id, and
                keys matching CountTypes name and count increment. Other keys
                are ignored.
        """
        counts = coerce_counts(counts)
        printing_id = counts.get('id')
        printing = self.collection.id_to_printing.get(printing_id)
        if printing is None:
            print('id not found for printing, searching')
            printing = find_printing(
                coll=self.collection, set_code=counts.get('set'),
                name=counts.get('name'), set_number=counts.get('number'),
                multiverseid=counts.get('multiverseid'), strict=strict)
            if printing is None:
                raise DeserializationError(
                    'Could not match id to known printing from counts: %r' %
                    counts)

        for counttype in models.CountTypes:
            countname = counttype.name
            count = counts.get(countname)
            if count:
                existing = printing.counts.get(counttype, 0)
                printing.counts[counttype] = existing + count

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
