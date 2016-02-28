"""Test helper providing access to test data."""

import json
import os
import unittest

MTGJSON_FILE = os.path.join(
    os.path.dirname(__file__), 'data', 'AllSets_testdata.json')


class MtgJsonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mtg_datafile = os.path.abspath(MTGJSON_FILE)
        with open(cls.mtg_datafile, 'r') as testdatafile:
            cls.mtg_data = json.load(testdatafile)

        cls.sets_data = cls.mtg_data

        cls.cards_data = {}
        for set_data in cls.sets_data.values():
            for card_data in set_data['cards']:
                cls.cards_data[card_data['id']] = card_data
