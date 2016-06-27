"""Tests for mtg_ssm.serialization.interface.py"""

import pytest

from mtg_ssm.mtg import card_db
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


TEST_PRINT_ID = '958ae1416f8f6287115ccd7c5c61f2415a313546'


@pytest.fixture  # todo: default scope?
def cdb(sets_data):
    """Fixture card_db with mtg json data."""
    return card_db.CardDb(sets_data)


def test_coerce_count():
    count = {'id': 'a', 'multiverseid': '12', 'copies': '4', 'foils': '5'}
    coerced_counts = interface.coerce_count(count)
    expected = {'id': 'a', 'multiverseid': 12, 'copies': 4, 'foils': 5}
    assert coerced_counts == expected


# build_print_count tests
def test_bpc_bad_printing(cdb):
    card_counts = [{}]
    with pytest.raises(interface.DeserializationError):
        interface.build_print_counts(cdb, card_counts)


def test_bpc_no_counts(cdb):
    card_counts = [{'id': TEST_PRINT_ID}]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert not print_counts


def test_bpc_zeros(cdb):
    card_counts = [{'id': TEST_PRINT_ID, 'copies': 0, 'foils': 0}]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert not print_counts


def test_bpc_once(cdb):
    print_ = cdb.id_to_printing[TEST_PRINT_ID]
    card_counts = [{'id': TEST_PRINT_ID, 'copies': 1, 'foils': 2}]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert print_counts == {
        print_: {
            models.CountTypes.copies: 1,
            models.CountTypes.foils: 2,
        }
    }


def test_bpc_with_find(cdb):
    print_ = cdb.id_to_printing[
        '536d407161fa03eddee7da0e823c2042a8fa0262']
    card_counts = [{'set': 'S00', 'name': 'Rhox', 'copies': 1}]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert print_counts == {
        print_: {models.CountTypes.copies: 1}
    }


def test_bpc_multiple(cdb):
    print1 = cdb.id_to_printing[TEST_PRINT_ID]
    print2 = cdb.id_to_printing[
        '536d407161fa03eddee7da0e823c2042a8fa0262']
    card_counts = [
        {'id': TEST_PRINT_ID, 'copies': 1, 'foils': 2},
        {'set': 'S00', 'name': 'Rhox', 'copies': 1},
    ]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert print_counts == {
        print1: {
            models.CountTypes.copies: 1,
            models.CountTypes.foils: 2,
        },
        print2: {models.CountTypes.copies: 1},
    }


def test_bpc_repeat(cdb):
    print_ = cdb.id_to_printing[TEST_PRINT_ID]
    card_counts = [
        {'id': TEST_PRINT_ID, 'copies': 4},
        {'id': TEST_PRINT_ID, 'copies': 3, 'foils': '8'},
    ]
    print_counts = interface.build_print_counts(cdb, card_counts)
    assert print_counts == {
        print_: {
            models.CountTypes.copies: 7,
            models.CountTypes.foils: 8,
        }
    }


@pytest.mark.parametrize('in_print_counts,out_print_counts', [
    ([], {}),
    ([{'a': {'b': 2}}], {'a': {'b': 2}}),
    ([{'a': {'b': 2}}, {'a': {'b': 1, 'c': 4}}], {'a': {'b': 3, 'c': 4}}),
    ([{'a': {'b': 2}}, {'a': {'c': 1}, 'b': {'c': 3}}, {'a': {'c': 5}}],
     {'a': {'b': 2, 'c': 6}, 'b': {'c': 3}}),
])
def test_merge_print_counts(in_print_counts, out_print_counts):
    assert interface.merge_print_counts(*in_print_counts) == out_print_counts


# Printing lookup tests
@pytest.mark.parametrize('set_code,name,set_number,multiverseid', [
    ('foo', 'bar', 'baz', 'quux'),  # not matching printing
    ('ICE', 'Forest', None, None),  # multiple matches
    ('foo', 'Abattoir Ghoul', '85', 222911),  # bad set_code
    ('ISD', 'foo', '85', 222911),  # bad name
])
def test_printing_not_found(cdb, set_code, name, set_number, multiverseid):
    printing = interface.find_printing(
        cdb=cdb, set_code=set_code, name=name, set_number=set_number,
        multiverseid=multiverseid)
    assert printing is None


@pytest.mark.parametrize('set_code,name,set_number,multiverseid,found_id', [
    # pylint: disable=line-too-long
    ('S00', 'Rhox', 'foo', 'bar', '536d407161fa03eddee7da0e823c2042a8fa0262'),
    ('pMGD', "Black Sun's Zenith", '7', 'foo', '6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc'),
    ('LEA', 'Forest', 'foo', 288, '5ede9781b0c5d157c28a15c3153a455d7d6180fa'),
    ('ISD', 'Abattoir Ghoul', '85', 222911, '958ae1416f8f6287115ccd7c5c61f2415a313546'),
])
def test_found_printing(cdb, set_code, name, set_number, multiverseid,
                        found_id):
    printing = interface.find_printing(
        cdb=cdb, set_code=set_code, name=name, set_number=set_number,
        multiverseid=multiverseid)
    assert printing.id_ == found_id
