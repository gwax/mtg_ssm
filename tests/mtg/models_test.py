"""Tests for mtg_ssm.mtg.models"""

import datetime as dt
from unittest import mock

from mtg_ssm.mtg import models

from tests.mtgjson import mtgjson_testcase


class ModelsTest(mtgjson_testcase.MtgJsonTestCase):

    def test_card(self):
        # Setup
        ag_card_data = self.cards_data[
            '958ae1416f8f6287115ccd7c5c61f2415a313546']
        # Execute
        card = models.Card(mock.sentinel.collection, ag_card_data)
        # Verify
        self.assertEqual(mock.sentinel.collection, card.collection)
        self.assertEqual('Abattoir Ghoul', card.name)
        self.assertFalse(card.strict_basic)

    def test_card_strict_basic(self):
        # Setup
        forest_data = self.cards_data[
            'c78d2da78c68c558b1adc734b3f164e885407ffc']
        snow_forest_data = self.cards_data[
            '5e9f08498a9343b1954103e493da2586be0fe394']
        ag_card_data = self.cards_data[
            '958ae1416f8f6287115ccd7c5c61f2415a313546']
        # Execute
        forest_card = models.Card(None, forest_data)
        snow_forest_card = models.Card(None, snow_forest_data)
        ag_card = models.Card(None, ag_card_data)
        # Verify
        self.assertTrue(forest_card.strict_basic)
        self.assertFalse(snow_forest_card.strict_basic)
        self.assertFalse(ag_card.strict_basic)

    def test_card_printing(self):
        # Setup
        ag_card_data = self.cards_data[
            '958ae1416f8f6287115ccd7c5c61f2415a313546']
        # Execute
        printing = models.CardPrinting(
            mock.sentinel.collection, 'ISD', ag_card_data)
        # Verify
        self.assertEqual(mock.sentinel.collection, printing.collection)
        self.assertEqual(
            '958ae1416f8f6287115ccd7c5c61f2415a313546', printing.id_)
        self.assertEqual('Abattoir Ghoul', printing.card_name)
        self.assertEqual('ISD', printing.set_code)
        self.assertEqual('85', printing.set_number)
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('Volkan Baga', printing.artist)
        self.assertEqual({}, printing.counts)
        self.assertEqual(85, printing.set_integer)
        self.assertEqual(None, printing.set_variant)

    def test_printing_letter_var(self):
        # Setup
        dlv_card_data = self.cards_data[
            '0b06d8d9e7662ada82bd29e1138d959978ba2280']
        ia_card_data = self.cards_data[
            'e5c4aa9a443c346ccbf8d99c9320138827065e05']
        # Execute
        dlv_printing = models.CardPrinting(None, 'ISD', dlv_card_data)
        ia_printing = models.CardPrinting(None, 'ISD', ia_card_data)
        # Verify
        self.assertEqual('Delver of Secrets', dlv_printing.card_name)
        self.assertEqual('Insectile Aberration', ia_printing.card_name)
        self.assertEqual('51a', dlv_printing.set_number)
        self.assertEqual('51b', ia_printing.set_number)
        self.assertEqual(51, dlv_printing.set_integer)
        self.assertEqual(51, ia_printing.set_integer)
        self.assertEqual('a', dlv_printing.set_variant)
        self.assertEqual('b', ia_printing.set_variant)

    def test_printing_star_variant(self):
        # Setup
        etc1_card_data = self.cards_data[
            '08fcfee6a7c4eddcd44e43e918cbf9d479492fe7']
        etc2_card_data = self.cards_data[
            '62ff415cafefac84a5bb7174cb7ef175c14625de']
        # Execut
        etc1_printing = models.CardPrinting(None, 'PLS', etc1_card_data)
        etc2_printing = models.CardPrinting(None, 'PLS', etc2_card_data)
        # Verify
        self.assertEqual('Ertai, the Corrupted', etc1_printing.card_name)
        self.assertEqual('Ertai, the Corrupted', etc2_printing.card_name)
        self.assertEqual('107', etc1_printing.set_number)
        self.assertEqual('★107', etc2_printing.set_number)
        self.assertEqual(107, etc1_printing.set_integer)
        self.assertEqual(107, etc2_printing.set_integer)
        self.assertEqual(None, etc1_printing.set_variant)
        self.assertEqual('★', etc2_printing.set_variant)

    def test_card_set(self):
        # Setup
        set_data = self.sets_data['PLS']
        # Execute
        card_set = models.CardSet(mock.sentinel.collection, set_data)
        # Verify
        self.assertEqual(mock.sentinel.collection, card_set.collection)
        self.assertEqual('PLS', card_set.code)
        self.assertEqual('Planeshift', card_set.name)
        self.assertEqual('Invasion', card_set.block)
        self.assertEqual(dt.date(2001, 2, 5), card_set.release_date)
        self.assertEqual('expansion', card_set.type_)
        self.assertFalse(card_set.online_only)
