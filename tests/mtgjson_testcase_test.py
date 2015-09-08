"""Test for mtgjson_testcase."""

from __future__ import absolute_import, unicode_literals
from builtins import super

from tests import mtgjson_testcase


class MtgJsonTestCaseTest(mtgjson_testcase.MtgJsonTestCase):

    def test_has_mtgjson(self):
        self.assertTrue(self.mtg_data)

    def test_lea(self):
        lea = self.mtg_data['LEA']
        self.assertIsInstance(lea, dict)

    def test_lea_cards(self):
        lea = self.mtg_data['LEA']
        lea_cards = lea['cards']
        self.assertIsInstance(lea_cards, list)

    def test_lea_air_elemental(self):
        lea = self.mtg_data['LEA']
        lea_cards = lea['cards']
        air_elemental = lea_cards[0]
        self.assertIsInstance(air_elemental, dict)
        self.assertEqual('Air Elemental', air_elemental['name'])
        self.assertEqual(94, air_elemental['multiverseid'])

    def test_chaotic_aether(self):
        chaotic_aether = self.mtg_data['PC2']['cards'][2]
        self.assertEqual('Chaotic \u00c6ther', chaotic_aether['name'])
