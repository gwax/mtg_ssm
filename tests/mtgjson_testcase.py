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
