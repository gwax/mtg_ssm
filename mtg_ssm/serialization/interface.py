"""Interface definition for serializers."""

import abc
import collections
from typing import Dict

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts


class Error(Exception):
    """Base error for serializers."""


class UnknownDialect(Exception):
    """Raised when an (extension, dialect) pair is requested."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


class SerializationDialect(metaclass=abc.ABCMeta):
    """Abstract interface for mtg ssm serialization dialect."""

    _dialects = []
    _dialect_registry = {}

    def __init__(self, cdb: card_db.CardDb) -> None:
        self.cdb = cdb

    @property
    @classmethod
    @abc.abstractmethod
    def extension(cls) -> str:
        """Registered file extension, excluding '.' """

    @property
    @classmethod
    @abc.abstractmethod
    def dialect(cls) -> str:
        """Registered dialect name.

        Note: a dialect that matches the extension will be considered the
            default dialect for that extension.
        """

    @abc.abstractmethod
    def write(self, filename: str, print_counts) -> None:
        """Write print counts to a file."""

    @abc.abstractmethod
    def read(self, filename: str) -> Dict[str, Dict[counts.CountTypes, int]]:
        """Read print counts from file."""

    @staticmethod
    def _register_dialects():
        """Register dialects for extensions from all subclasses."""
        dialects = []
        registry = {}
        subclasses = collections.deque(SerializationDialect.__subclasses__())
        while subclasses:
            klass = subclasses.popleft()
            if not klass.__abstractmethods__:
                registry[(klass.extension, klass.dialect)] = klass
                dialects.append((klass.extension, klass.dialect, klass.__doc__))
            subclasses.extend(klass.__subclasses__())
        dialects.sort()

        SerializationDialect._dialects = dialects
        SerializationDialect._dialect_registry = registry

    @staticmethod
    def dialects():
        """List of (extension, dialect, description) of registered dialects."""
        if not SerializationDialect._dialects:
            SerializationDialect._register_dialects()
        return SerializationDialect._dialects

    @staticmethod
    def by_extension(extension, dialect_mappings):
        """Get a serializer class for a given extension and dialect mapping."""
        if not extension:
            raise UnknownDialect(
                "Filename has no extension, cannot determine output format"
            )
        if not SerializationDialect._dialect_registry:
            SerializationDialect._register_dialects()
        dialect = dialect_mappings.get(extension, extension)
        try:
            return SerializationDialect._dialect_registry[(extension, dialect)]
        except KeyError:
            raise UnknownDialect(
                'File extension: "{ext}" dialect: "{dia}" not found in registry'.format(
                    ext=extension, dia=dialect
                )
            )
