"""Test helper providing access to test data."""

import json
import os
import unittest

MTGJSON_FILE = 'testdata/AllSets_testdata.json'


class MtgJsonTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basepath = os.path.dirname(__file__)
        cls.mtg_datafile = os.path.join(basepath, MTGJSON_FILE)
        with open(cls.mtg_datafile, 'r') as testdatafile:
            cls.mtg_data = json.load(testdatafile)
