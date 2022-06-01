"""Interface definition for serializers."""

import abc
from pathlib import Path
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Type

from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.indexes import Oracle


class Error(Exception):
    """Base error for serializers."""


class UnknownDialect(Exception):
    """Raised when an (extension, dialect) pair is requested."""


class DeserializationError(Error):
    """Raised when there is an error reading counts from a file."""


class SerializationDialect(metaclass=abc.ABCMeta):
    """Abstract interface for mtg ssm serialization dialect."""

    _EXT_DIALECT_DOC: ClassVar[Set[Tuple[str, str, str]]] = set()
    _EXT_DIALECT_TO_IMPL: ClassVar[
        Dict[Tuple[str, str], Type["SerializationDialect"]]
    ] = {}

    extension: ClassVar[Optional[str]] = None
    dialect: ClassVar[Optional[str]] = None

    def __init_subclass__(cls: Type["SerializationDialect"]) -> None:
        super().__init_subclass__()
        if cls.extension is not None and cls.dialect is not None:
            cls._EXT_DIALECT_DOC.add(
                (cls.extension, cls.dialect, cls.__doc__ or cls.__name__)
            )
            cls._EXT_DIALECT_TO_IMPL[(cls.extension, cls.dialect)] = cls

    @abc.abstractmethod
    def write(self, path: Path, collection: MagicCollection) -> None:
        """Write print counts to a file."""

    @abc.abstractmethod
    def read(self, path: Path, oracle: Oracle) -> MagicCollection:
        """Read print counts from file."""

    @classmethod
    def dialects(
        cls: Type["SerializationDialect"],
    ) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """List of (extension, dialect, description) of registered dialects."""
        return sorted(
            (ext, dial or "", doc or "") for ext, dial, doc in cls._EXT_DIALECT_DOC
        )

    @classmethod
    def by_extension(
        cls: Type["SerializationDialect"],
        extension: str,
        dialect_mappings: Dict[str, str],
    ) -> Type["SerializationDialect"]:
        """Get a serializer class for a given extension and dialect mapping."""
        dialect = dialect_mappings.get(extension, extension)
        try:
            return cls._EXT_DIALECT_TO_IMPL[(extension, dialect)]
        except KeyError as err:
            raise UnknownDialect(
                f'File extension: "{extension}" dialect: "{dialect}" not found in registry'
            ) from err
