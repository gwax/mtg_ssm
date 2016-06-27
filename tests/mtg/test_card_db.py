"""Tests for mtg_ssm.mtg.card_db"""

from mtg_ssm.mtg import card_db


def test_load_mtgjson(sets_data):
    # Setup
    isd_mtg_data = {
        k: v for k, v in sets_data.items() if k == 'ISD'}
    # Execute
    cdb = card_db.CardDb()
    cdb.load_mtg_json(isd_mtg_data)
    # Verify
    name_to_name = {n: c.name for n, c in cdb.name_to_card.items()}
    expected_name_to_name = {
        'Abattoir Ghoul': 'Abattoir Ghoul',
        'Delver of Secrets': 'Delver of Secrets',
        'Insectile Aberration': 'Insectile Aberration',
        'Forest': 'Forest',
    }
    assert name_to_name == expected_name_to_name

    code_to_setname = {c: s.name for c, s in cdb.code_to_card_set.items()}
    expected_code_to_setname = {
        'ISD': 'Innistrad',
    }
    assert code_to_setname == expected_code_to_setname

    setname_to_setcode = {
        n: s.code for n, s in cdb.setname_to_card_set.items()}
    expected_setname_to_code = {
        'Innistrad': 'ISD',
    }
    assert setname_to_setcode == expected_setname_to_code

    id_to_setnum = {i: p.set_number for i, p in cdb.id_to_printing.items()}
    expected_id_to_setnum = {
        '0b06d8d9e7662ada82bd29e1138d959978ba2280': '51a',
        'e5c4aa9a443c346ccbf8d99c9320138827065e05': '51b',
        '958ae1416f8f6287115ccd7c5c61f2415a313546': '85',
        'e9abef8533c9ce6549147232c5fceff75ffb460a': '262',
        '3c509643d7f7827b2debf968c05cb800cb772360': '263',
        'd5dbd9b201a515d119b424b3d7b06dcf30a5c675': '264',
    }
    assert id_to_setnum == expected_id_to_setnum


def test_without_online_only(sets_data):
    # Execute
    cdb = card_db.CardDb()
    cdb.load_mtg_json(sets_data)
    # Verify
    expected_set_codes = {
        'LEA',
        'FEM',
        'S00',
        'ICE',
        'pMGD',
        'HML',
        'ISD',
        'ARC',
        'HOP',
        'PC2',
        'MMA',
        'pMEI',
        'PLS',
        'PLC',
        'OGW',
        'CHK',
        'W16',
    }
    assert cdb.code_to_card_set.keys() == expected_set_codes


def test_with_online_only(sets_data):
    # Execute
    cdb = card_db.CardDb()
    cdb.load_mtg_json(sets_data, include_online_only=True)
    # Verify
    expected_set_codes = {
        'LEA',
        'FEM',
        'S00',
        'ICE',
        'VMA',
        'pMGD',
        'HML',
        'ISD',
        'ARC',
        'HOP',
        'PC2',
        'MMA',
        'pMEI',
        'PLS',
        'PLC',
        'OGW',
        'CHK',
        'W16',
    }
    assert cdb.code_to_card_set.keys() == expected_set_codes


def test_rebuild_indexes(sets_data):
    # Setup
    cdb = card_db.CardDb()
    cdb.load_mtg_json(sets_data)
    # Execute
    cdb.rebuild_indexes()
    # Verify
    isd_ids = {p.id_ for p in cdb.set_code_to_printings['ISD']}
    expected_ids = {
        '0b06d8d9e7662ada82bd29e1138d959978ba2280',
        'e5c4aa9a443c346ccbf8d99c9320138827065e05',
        '958ae1416f8f6287115ccd7c5c61f2415a313546',
        'e9abef8533c9ce6549147232c5fceff75ffb460a',
        '3c509643d7f7827b2debf968c05cb800cb772360',
        'd5dbd9b201a515d119b424b3d7b06dcf30a5c675',
    }
    assert isd_ids == expected_ids

    darkrit_ids = {
        p.id_ for p in cdb.card_name_to_printings['Dark Ritual']}
    expected_ids = {
        'fff0b8e8fea06ee1ac5c35f048a0a459b1222673',
        '2fab0ea29e3bbe8bfbc981a4c8163f3e7d267853',
        '19c38ff78c0e98b38f3bd8184478e22152d9a624',
    }
    assert darkrit_ids == expected_ids

    snnm_keys = [
        ('ISD', 'Abattoir Ghoul', '85', 222911),
        ('ISD', 'Abattoir Ghoul', None, 222911),
        ('ISD', 'Abattoir Ghoul', '85', None),
        ('ISD', 'Abattoir Ghoul', None, None),
    ]
    for snnm_key in snnm_keys:
        found_print_ids = {
            p.id_ for p in cdb.set_name_num_mv_to_printings[snnm_key]}
        assert found_print_ids == {'958ae1416f8f6287115ccd7c5c61f2415a313546'}


def test_sort_indexes(sets_data):
    # Setup
    cdb = card_db.CardDb()
    cdb.load_mtg_json(sets_data)
    cdb.rebuild_indexes()
    # Execute
    cdb.sort_indexes()
    # Verify
    forest_set_and_mvid = [
        (p.set_code, p.multiverseid)
        for p in cdb.card_name_to_printings['Forest']]
    expected = [
        ('ICE', 2746),
        ('ICE', 2747),
        ('ICE', 2748),
        ('ISD', 245247),
        ('ISD', 245248),
        ('ISD', 245246),
        ('LEA', 288),
        ('LEA', 289),
    ]
    assert forest_set_and_mvid == expected

    isd_set_numbers = [
        p.set_number for p in cdb.set_code_to_printings['ISD']]
    expected = [
        '51a',
        '51b',
        '85',
        '262',
        '263',
        '264',
    ]
    assert isd_set_numbers == expected
