"""Interface definition for serializers."""

import abc
from typing import Any, Dict, Set

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models


class Error(Exception):
    """Base error for serializers."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


class MtgSsmSerializer(metaclass=abc.ABCMeta):
    """Abstract interface for a mtg ssm serializer."""

    def __init__(self, coll: collection.Collection):
        self.collection = coll

    @property
    @abc.abstractmethod
    def extensions(self) -> Set[str]:
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
        printing_id = counts.get('id')
        printing = self.collection.id_to_printing.get(printing_id)
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
