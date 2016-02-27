"""Tests for mtg_ssm.mtgcsv"""

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models
from mtg_ssm.serialization import mtgdict

from tests.mtgjson import mtgjson_testcase


class MtgDictTest(mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        self.collection = collection.Collection()
        self.collection.load_mtg_json(self.mtg_data)
        self.collection.rebuild_indexes()

    def test_get_printing_not_found(self):
        # Setup
        card_dict = {}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertIsNone(printing)

    def test_get_printing_set_and_name(self):
        # Setup
        card_dict = {'set': 'ISD', 'name': 'Abattoir Ghoul'}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertEqual(
            '958ae1416f8f6287115ccd7c5c61f2415a313546', printing.id_)

    def test_get_printing_set_name_num(self):
        # Setup
        card_dict = {'set': 'ISD', 'name': 'Forest', 'number': '263'}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertEqual(
            '3c509643d7f7827b2debf968c05cb800cb772360', printing.id_)

    def test_get_printing_set_name_mv(self):
        # Setup
        card_dict = {'set': 'ISD', 'name': 'Forest', 'multiverseid': 245248}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertEqual(
            '3c509643d7f7827b2debf968c05cb800cb772360', printing.id_)

    def test_get_set_name_num_mv(self):
        # Setup
        card_dict = {'set': 'HML', 'name': 'Cemetery Gate', 'number': None,
                     'multiverseid': 2913}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertEqual(
            'f7a1292dac99aa861d3f501653969595ed12038c', printing.id_)

    def test_get_printing_none_set(self):
        # Setup
        card_dict = {'name': 'Abattoir Ghoul'}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_none_name(self):
        # Setup
        card_dict = {'set': 'ISD'}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertIsNone(printing)

    def test_get_printing_by_id(self):
        # Setup
        card_dict = {'id': '958ae1416f8f6287115ccd7c5c61f2415a313546'}
        # Execute
        printing = mtgdict.get_printing(self.collection, card_dict)
        # Verify
        self.assertEqual(
            '958ae1416f8f6287115ccd7c5c61f2415a313546', printing.id_)

    def test_load_counts(self):
        # Setup
        card_dicts = [  # pylint: disable=line-too-long
            {'id': 'e9abef8533c9ce6549147232c5fceff75ffb460a', 'copies': 1},
            {'id': '3c509643d7f7827b2debf968c05cb800cb772360', 'foils': 2},
            {'id': 'd5dbd9b201a515d119b424b3d7b06dcf30a5c675', 'copies': 3, 'foils': 4},
        ]
        # Execute
        mtgdict.load_counts(self.collection, card_dicts)
        # Verify
        id_to_counts = {
            p.id_: p.counts for p in self.collection.id_to_printing.values()
            if p.counts
        }
        expected = {
            'e9abef8533c9ce6549147232c5fceff75ffb460a': {
                models.CountTypes.copies: 1,
            },
            '3c509643d7f7827b2debf968c05cb800cb772360': {
                models.CountTypes.foils: 2,
            },
            'd5dbd9b201a515d119b424b3d7b06dcf30a5c675': {
                models.CountTypes.copies: 3,
                models.CountTypes.foils: 4,
            },
        }
        self.assertEqual(expected, id_to_counts)

    def test_load_counts_add_more(self):
        # Setup
        preload_card_dicts = [  # pylint: disable=line-too-long
            {'id': 'e9abef8533c9ce6549147232c5fceff75ffb460a', 'copies': 1},
            {'id': '3c509643d7f7827b2debf968c05cb800cb772360', 'foils': 2},
            {'id': 'd5dbd9b201a515d119b424b3d7b06dcf30a5c675', 'copies': 3, 'foils': 4},
        ]
        mtgdict.load_counts(self.collection, preload_card_dicts)
        card_dicts = [
            {'id': 'e9abef8533c9ce6549147232c5fceff75ffb460a', 'copies': None},
            {'id': '3c509643d7f7827b2debf968c05cb800cb772360', 'copies': 5},
            {'id': 'd5dbd9b201a515d119b424b3d7b06dcf30a5c675', 'copies': 6, 'foils': 7},
        ]
        # Execute
        mtgdict.load_counts(self.collection, card_dicts)
        # Verify
        id_to_counts = {
            p.id_: p.counts for p in self.collection.id_to_printing.values()
            if p.counts
        }
        expected = {
            'e9abef8533c9ce6549147232c5fceff75ffb460a': {
                models.CountTypes.copies: 1,
            },
            '3c509643d7f7827b2debf968c05cb800cb772360': {
                models.CountTypes.foils: 2, models.CountTypes.copies: 5
            },
            'd5dbd9b201a515d119b424b3d7b06dcf30a5c675': {
                models.CountTypes.copies: 9,
                models.CountTypes.foils: 11,
            },
        }
        self.assertEqual(expected, id_to_counts)
