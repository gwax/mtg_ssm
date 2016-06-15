"""Test for mtgjson_testcase."""


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
    chaotic_aether = cards_data['5669523e75ffdb436b768d4dd37cb95b82919d51']
    assert chaotic_aether['name'] == 'Chaotic \u00c6ther'
