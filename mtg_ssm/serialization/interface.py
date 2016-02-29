"""Interface definition for serializers."""

import abc
from typing import Set

from mtg_ssm.mtg import collection


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
