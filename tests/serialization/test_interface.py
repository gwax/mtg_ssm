"""Tests for mtg_ssm.serialization.interface.py"""

from unittest import mock

import pytest

from mtg_ssm.serialization import interface


# Subclass registration tests
def test_all_dialects():
    all_formats = interface.SerializationDialect.dialects()
    assert sorted(all_formats) == [
        ('csv', 'csv', mock.ANY),
        ('csv', 'deckbox', mock.ANY),
        ('csv', 'terse', mock.ANY),
        ('xlsx', 'xlsx', mock.ANY),
    ]


@pytest.mark.parametrize('extension,dialect_mapping,dialect_name', [
    ('csv', {}, 'CsvFullDialect'),
    ('csv', {'csv': 'csv'}, 'CsvFullDialect'),
    ('csv', {'csv': 'terse'}, 'CsvTerseDialect'),
    ('csv', {'csv': 'deckbox'}, 'DeckboxCsvDialect'),
    ('csv', {'xlsx': 'csv'}, 'CsvFullDialect'),
    ('xlsx', {}, 'XlsxDialect'),
    ('xlsx', {'xlsx': 'xlsx'}, 'XlsxDialect'),
    pytest.mark.xfail(
        ('invalid', {}, mock.ANY),
        raises=interface.UnknownDialect),
    pytest.mark.xfail(
        ('', {}, mock.ANY),
        raises=interface.UnknownDialect),
])
def test_extension_lookup(extension, dialect_mapping, dialect_name):
    serialization_class = interface.SerializationDialect.by_extension(
        extension, dialect_mapping)
    assert isinstance(serialization_class, type)
    assert issubclass(serialization_class, interface.SerializationDialect)
    assert serialization_class.__name__ == dialect_name
