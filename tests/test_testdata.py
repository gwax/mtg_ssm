"""Test for mtgjson_testcase."""

import pytest

from tests import gen_testdata


def test_sets_data(sets_data):
    assert sets_data
    assert isinstance(sets_data['LEA'], dict)
    assert isinstance(sets_data['LEA']['cards'], list)


def test_cards_data(cards_data):
    assert cards_data


def test_lea_air_elemental(sets_data, cards_data):
    [air_elemental] = [
        c for c in sets_data['LEA']['cards']
        if c['id'] == '926234c2fe8863f49220a878346c4c5ca79b6046']
    assert air_elemental is \
        cards_data['926234c2fe8863f49220a878346c4c5ca79b6046']
    assert isinstance(air_elemental, dict)
    assert air_elemental['name'] == 'Air Elemental'
    assert air_elemental['multiverseid'] == 94


def test_chaotic_aether(cards_data):
    chaotic_aether = cards_data['c98cdec5d2201abe3411db460cb088b82945bb9e']
    assert chaotic_aether['name'] == 'Chaotic Aether'


@pytest.mark.parametrize('mtgjid, name', [
    ('c98cdec5d2201abe3411db460cb088b82945bb9e', 'Chaotic Aether'),
    ('5933bb74b618a4e4f61eb4b5b55b416c11affd11', 'Bushi Tenderfoot'),
    ('b955500d1a3e0c4b36e3cbf6332c3bca4597eaee', 'Kenzo the Hardhearted'),
    ('284c1af34bceb74c211ca1f314e76f95030299d4', 'Faithful Squire'),
    ('0b9a826470865b4e67039d0bc606d856d69e30b3', 'Kaiso, Memory of Loyalty'),
])
def test_card_ids(cards_data, mtgjid, name):
    assert cards_data[mtgjid]['name'] == name


def test_all_sets_and_cards(sets_data):
    sets_to_cards = {}
    for setcode, setdata in sets_data.items():
        sets_to_cards[setcode] = {c['name'] for c in setdata['cards']}
    assert sets_to_cards == gen_testdata.TEST_SETS_TO_CARDS
