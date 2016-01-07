"""Test for mtgjson_testcase."""

from tests.mtgjson import mtgjson_testcase


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
        [air_elemental] = [
            c for c in self.mtg_data['LEA']['cards']
            if c['id'] == '926234c2fe8863f49220a878346c4c5ca79b6046']
        self.assertIsInstance(air_elemental, dict)
        self.assertEqual('Air Elemental', air_elemental['name'])
        self.assertEqual(94, air_elemental['multiverseid'])

    def test_chaotic_aether(self):
        [chaotic_aether] = [
            c for c in self.mtg_data['PC2']['cards']
            if c['id'] == '5669523e75ffdb436b768d4dd37cb95b82919d51']
        self.assertEqual('Chaotic \u00c6ther', chaotic_aether['name'])
