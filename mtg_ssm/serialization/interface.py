"""Interface definition for serializers."""

import abc
import collections
from typing import Dict

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts
from mtg_ssm.mtg import models


class Error(Exception):
    """Base error for serializers."""


class InvalidExtensionOrFormat(Error):
    """Raised if an invalid extension or format is provided."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


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
            models.CardPrinting, Dict[counts.CountTypes, int]]:
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
