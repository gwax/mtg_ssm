"""Tests for mtg_ssm.serialization.interface.py"""

from typing import Dict
from unittest import mock

import pytest

from mtg_ssm.serialization import interface


# Subclass registration tests
def test_all_dialects() -> None:
    all_formats = interface.SerializationDialect.dialects()
    assert sorted(all_formats) == [
        ("csv", "csv", mock.ANY),
        ("csv", "terse", mock.ANY),
        ("xlsx", "xlsx", mock.ANY),
    ]


@pytest.mark.parametrize(
    "extension, dialect_mapping, dialect_name",
    [
        pytest.param("csv", {}, "CsvFullDialect"),
        pytest.param("csv", {"csv": "terse"}, "CsvTerseDialect"),
        pytest.param("csv", {"xlsx": "csv"}, "CsvFullDialect"),
        pytest.param("xlsx", {}, "XlsxDialect"),
        pytest.param(
            "invalid",
            {},
            mock.ANY,
            marks=pytest.mark.xfail(raises=interface.UnknownDialect),
        ),
        pytest.param(
            "", {}, mock.ANY, marks=pytest.mark.xfail(raises=interface.UnknownDialect)
        ),
    ],
)
def test_extension_lookup(
    extension: str, dialect_mapping: Dict[str, str], dialect_name: str
) -> None:
    serialization_class = interface.SerializationDialect.by_extension(
        extension, dialect_mapping
    )
    assert isinstance(serialization_class, type)
    assert issubclass(serialization_class, interface.SerializationDialect)
    assert serialization_class.__name__ == dialect_name
