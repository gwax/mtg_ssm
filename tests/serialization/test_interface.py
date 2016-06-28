"""Tests for mtg_ssm.serialization.interface.py"""

import pytest

from mtg_ssm.serialization import interface


# Subclass registration tests
def test_all_formats():
    all_formats = interface.MtgSsmSerializer.all_formats()
    expected = {'auto', 'csv', 'xlsx', 'deckbox'}
    assert set(all_formats) == expected
    assert all_formats[0] == 'auto'


@pytest.mark.parametrize('extension,ser_format,name', [
    ('.csv', 'auto', 'MtgCsvSerializer'),
    (None, 'csv', 'MtgCsvSerializer'),
    ('.xlsx', 'auto', 'MtgXlsxSerializer'),
    (None, 'xlsx', 'MtgXlsxSerializer'),
    (None, 'deckbox', 'MtgDeckboxSerializer'),
])
def test_serializer_lookup(extension, ser_format, name):
    serializer_class = interface.MtgSsmSerializer.by_extension_and_format(
        extension, ser_format)
    assert isinstance(serializer_class, type)
    assert serializer_class.__name__ == name


@pytest.mark.parametrize('extension,ser_format', [
    ('', 'auto'),
    (None, 'foo'),
])
def test_serializer_lookup_invalid(extension, ser_format):
    with pytest.raises(interface.InvalidExtensionOrFormat):
        interface.MtgSsmSerializer.by_extension_and_format(
            extension, ser_format)
