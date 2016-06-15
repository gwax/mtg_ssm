"""Tests for mtg_ssm.serialization.interface.py"""

import pytest

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models
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


# Count loading tests
class StubSerializer(interface.MtgSsmSerializer):
    """Stub serializer for testing purposes."""

    format = None
    extension = None
    write_to_file = None
    read_from_file = None


TEST_PRINT_ID = '958ae1416f8f6287115ccd7c5c61f2415a313546'


@pytest.fixture  # todo: default scope?
def coll(sets_data):
    """Fixture collection with mtg json data."""
    return collection.Collection(sets_data)


@pytest.fixture  # todo: default scope?
def stub_serializer(coll):
    """Fixture for StubSerializer instance bound to coll."""
    return StubSerializer(coll)


def test_coerce_counts():
    counts = {'id': 'a', 'multiverseid': '12', 'copies': '4', 'foils': '5'}
    coerced_counts = interface.coerce_counts(counts)
    expected = {'id': 'a', 'multiverseid': 12, 'copies': 4, 'foils': 5}
    assert coerced_counts == expected


def test_bad_printing(stub_serializer):
    counts = {}
    with pytest.raises(interface.DeserializationError):
        stub_serializer.load_counts(counts)


def test_load_nothing(coll, stub_serializer):
    counts = {'id': TEST_PRINT_ID}
    stub_serializer.load_counts(counts)
    assert not coll.id_to_printing[TEST_PRINT_ID].counts


def test_load_zeros(coll, stub_serializer):
    counts = {'id': TEST_PRINT_ID, 'copies': 0, 'foils': 0}
    stub_serializer.load_counts(counts)
    assert not coll.id_to_printing[TEST_PRINT_ID].counts


def test_load_counts(coll, stub_serializer):
    counts = {'id': TEST_PRINT_ID, 'copies': 1, 'foils': 2}
    stub_serializer.load_counts(counts)
    expected = {
        models.CountTypes.copies: 1,
        models.CountTypes.foils: 2,
    }
    assert coll.id_to_printing[TEST_PRINT_ID].counts == expected


def test_load_with_find(coll, stub_serializer):
    counts = {'set': 'S00', 'name': 'Rhox', 'copies': 1}
    stub_serializer.load_counts(counts)
    printing = coll.id_to_printing[
        '536d407161fa03eddee7da0e823c2042a8fa0262']
    assert printing.counts == {models.CountTypes.copies: 1}


def test_increase_counts(coll, stub_serializer):
    coll.id_to_printing[TEST_PRINT_ID].counts = {
        models.CountTypes.copies: 1,
        models.CountTypes.foils: 2,
    }
    counts = {'id': TEST_PRINT_ID, 'copies': 4, 'foils': '8'}
    stub_serializer.load_counts(counts)
    expected = {
        models.CountTypes.copies: 5,
        models.CountTypes.foils: 10,
    }
    assert coll.id_to_printing[TEST_PRINT_ID].counts == expected


# Printing lookup tests
@pytest.mark.parametrize('set_code,name,set_number,multiverseid', [
    ('foo', 'bar', 'baz', 'quux'),  # not matching printing
    ('ICE', 'Forest', None, None),  # multiple matches
    ('foo', 'Abattoir Ghoul', '85', 222911),  # bad set_code
    ('ISD', 'foo', '85', 222911),  # bad name
])
def test_printing_not_found(coll, set_code, name, set_number, multiverseid):
    printing = interface.find_printing(
        coll=coll, set_code=set_code, name=name, set_number=set_number,
        multiverseid=multiverseid)
    assert printing is None


@pytest.mark.parametrize('set_code,name,set_number,multiverseid,found_id', [
    # pylint: disable=line-too-long
    ('S00', 'Rhox', 'foo', 'bar', '536d407161fa03eddee7da0e823c2042a8fa0262'),
    ('pMGD', "Black Sun's Zenith", '7', 'foo', '6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc'),
    ('LEA', 'Forest', 'foo', 288, '5ede9781b0c5d157c28a15c3153a455d7d6180fa'),
    ('ISD', 'Abattoir Ghoul', '85', 222911, '958ae1416f8f6287115ccd7c5c61f2415a313546'),
])
def test_found_printing(coll, set_code, name, set_number, multiverseid,
                        found_id):
    printing = interface.find_printing(
        coll=coll, set_code=set_code, name=name, set_number=set_number,
        multiverseid=multiverseid)
    assert printing.id_ == found_id
