"""Interface definition for serializers."""

import abc
from typing import Any, Dict

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models


class Error(Exception):
    """Base error for serializers."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


def find_printing(coll, set_code, name, set_number, multiverseid):
    """Attempt to find a CardPrinting from given parameters."""
    found_printings = coll.set_name_num_mv_to_printings.get(
        (set_code, name, set_number, multiverseid), [])
    if len(found_printings) == 1:
        return found_printings[0]

    found_printings = coll.set_name_mv_to_printings.get(
        (set_code, name, multiverseid), [])
    if len(found_printings) == 1:
        return found_printings[0]

    found_printings = coll.set_name_num_to_printings.get(
        (set_code, name, set_number), [])
    if len(found_printings) == 1:
        return found_printings[0]

    found_printings = coll.set_and_name_to_printings.get(
        (set_code, name), [])
    if len(found_printings) == 1:
        return found_printings[0]

    return None


def coerce_counts(counts_dict):
    """Given a counts dict, coerce types to match desired input."""
    if 'multiverseid' in counts_dict:
        try:
            counts_dict['multiverseid'] = int(counts_dict['multiverseid'])
        except TypeError:
            pass
    for counttype in models.CountTypes:
        countname = counttype.name
        if countname in counts_dict:
            try:
                counts_dict[countname] = int(counts_dict[countname])
            except TypeError:
                pass
    return counts_dict


class MtgSsmSerializer(metaclass=abc.ABCMeta):
    """Abstract interface for a mtg ssm serializer."""

    def __init__(self, coll: collection.Collection):
        self.collection = coll

    @property
    @abc.abstractmethod
    def extension(self) -> str:
        """File extensions handled by this serializer."""

    @abc.abstractmethod
    def write_to_file(self, filename: str) -> None:
        """Write the collection to a file."""

    @abc.abstractmethod
    def read_from_file(self, filename: str) -> None:
        """Read counts from file and add them to the collection."""

    def load_counts(self, counts: Dict[Any, Any]) -> None:
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
                multiverseid=counts.get('multiverseid'))
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
