"""Tests for mtg_ssm.mtg.collection"""

from mtg_ssm.mtg import collection

from tests.mtgjson import mtgjson_testcase

# remeber to test sorting of None and '★' for indexes


class CollectionTest(mtgjson_testcase.MtgJsonTestCase):

    def test_load_mtgjson(self):
        # Setup
        isd_mtg_data = {
            k: v for k, v in self.mtg_data.items() if k == 'ISD'}
        # Execute
        coll = collection.Collection()
        coll.load_mtg_json(isd_mtg_data)
        # Verify
        name_to_name = {n: c.name for n, c in coll.name_to_card.items()}
        expected_name_to_name = {
            'Abattoir Ghoul': 'Abattoir Ghoul',
            'Delver of Secrets': 'Delver of Secrets',
            'Insectile Aberration': 'Insectile Aberration',
            'Forest': 'Forest',
        }
        self.assertEqual(expected_name_to_name, name_to_name)

        code_to_setname = {c: s.name for c, s in coll.code_to_card_set.items()}
        expected_code_to_setname = {
            'ISD': 'Innistrad',
        }
        self.assertEqual(expected_code_to_setname, code_to_setname)

        id_to_setnum = {i: p.set_number for i, p in coll.id_to_printing.items()}
        expected_id_to_setnum = {
            '0b06d8d9e7662ada82bd29e1138d959978ba2280': '51a',
            'e5c4aa9a443c346ccbf8d99c9320138827065e05': '51b',
            '958ae1416f8f6287115ccd7c5c61f2415a313546': '85',
            'e9abef8533c9ce6549147232c5fceff75ffb460a': '262',
            '3c509643d7f7827b2debf968c05cb800cb772360': '263',
            'd5dbd9b201a515d119b424b3d7b06dcf30a5c675': '264',
        }
        self.assertEqual(expected_id_to_setnum, id_to_setnum)

    def test_without_online_only(self):
        # Execute
        coll = collection.Collection()
        coll.load_mtg_json(self.mtg_data)
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
        }
        self.assertEqual(expected_set_codes, coll.code_to_card_set.keys())

    def test_with_online_only(self):
        # Execute
        coll = collection.Collection()
        coll.load_mtg_json(self.mtg_data, include_online_only=True)
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
        }
        self.assertEqual(expected_set_codes, coll.code_to_card_set.keys())

    def test_rebuild_indexes(self):
        # Setup
        coll = collection.Collection()
        coll.load_mtg_json(self.mtg_data)
        # Execute
        coll.rebuild_indexes()
        # Verify
        isd_ids = {p.id_ for p in coll.set_code_to_printings['ISD']}
        expected_ids = {
            '0b06d8d9e7662ada82bd29e1138d959978ba2280',
            'e5c4aa9a443c346ccbf8d99c9320138827065e05',
            '958ae1416f8f6287115ccd7c5c61f2415a313546',
            'e9abef8533c9ce6549147232c5fceff75ffb460a',
            '3c509643d7f7827b2debf968c05cb800cb772360',
            'd5dbd9b201a515d119b424b3d7b06dcf30a5c675',
        }
        self.assertEqual(expected_ids, isd_ids)

        darkrit_ids = {
            p.id_ for p in coll.card_name_to_printings['Dark Ritual']}
        expected_ids = {
            'fff0b8e8fea06ee1ac5c35f048a0a459b1222673',
            '2fab0ea29e3bbe8bfbc981a4c8163f3e7d267853',
            '19c38ff78c0e98b38f3bd8184478e22152d9a624',
        }
        self.assertEqual(expected_ids, darkrit_ids)

        snnm = ('ISD', 'Abattoir Ghoul', '85', 222911)
        snnm_ids = {p.id_ for p in coll.set_name_num_mv_to_printings[snnm]}
        expected_ids = {'958ae1416f8f6287115ccd7c5c61f2415a313546'}
        self.assertEqual(expected_ids, snnm_ids)

        snm = ('ISD', 'Abattoir Ghoul', 222911)
        snm_ids = {p.id_ for p in coll.set_name_mv_to_printings[snm]}
        expected_ids = {'958ae1416f8f6287115ccd7c5c61f2415a313546'}
        self.assertEqual(expected_ids, snm_ids)

        snn = ('ISD', 'Abattoir Ghoul', '85')
        snn_ids = {p.id_ for p in coll.set_name_num_to_printings[snn]}
        expected_ids = {'958ae1416f8f6287115ccd7c5c61f2415a313546'}
        self.assertEqual(expected_ids, snn_ids)

        san = ('ISD', 'Abattoir Ghoul')
        san_ids = {p.id_ for p in coll.set_and_name_to_printings[san]}
        expected_ids = {'958ae1416f8f6287115ccd7c5c61f2415a313546'}
        self.assertEqual(expected_ids, san_ids)

    def test_sort_indexes(self):
        # Setup
        coll = collection.Collection()
        coll.load_mtg_json(self.mtg_data)
        coll.rebuild_indexes()
        # Execute
        coll.sort_indexes()
        # Verify
        forest_set_and_mvid = [
            (p.set_code, p.multiverseid)
            for p in coll.card_name_to_printings['Forest']]
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
        self.assertEqual(expected, forest_set_and_mvid)

        isd_set_numbers = [
            p.set_number for p in coll.set_code_to_printings['ISD']]
        expected = [
            '51a',
            '51b',
            '85',
            '262',
            '263',
            '264',
        ]
        self.assertEqual(expected, isd_set_numbers)
