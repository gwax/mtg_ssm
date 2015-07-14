"""Tests for mtgcdb.mtgcsv"""

from mtgcdb import models
from mtgcdb import mtgcsv
from mtgcdb import mtgjson

from tests import mtgjson_testcase
from tests import sqlite_testcase


class MtgCsvTest(
    sqlite_testcase.SqliteTestCase, mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()

    def test_get_header(self):
        # Execute
        header = mtgcsv.header()

        # Verify
        self.assertEqual(['set', 'name', 'number', 'multiverseid'], header)

    def test_get_rows(self):
        # Execute
        rows = list(mtgcsv.get_rows(self.session))

        # Verify
        expected = [
            {'set': 'LEA', 'name': 'Air Elemental', 'multiverseid': 94, 'number': None},
            {'set': 'LEA', 'name': 'Forest', 'multiverseid': 288, 'number': None},
            {'set': 'LEA', 'name': 'Forest', 'multiverseid': 289, 'number': None},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2746, 'number': None},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2747, 'number': None},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2748, 'number': None},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': 2749, 'number': None},
            {'set': 'HML', 'name': 'Cemetery Gate', 'multiverseid': 2913, 'number': None},
            {'set': 'HML', 'name': 'Cemetery Gate', 'multiverseid': 2914, 'number': None},
            {'set': 'S00', 'name': 'Rhox', 'multiverseid': None, 'number': None},
            {'set': 'pMGD', 'name': 'Black Sun\'s Zenith', 'multiverseid': None, 'number': '7'},
            {'set': 'HOP', 'name': 'Academy at Tolaria West', 'multiverseid': 198073,
             'number': '1'},
            {'set': 'HOP', 'name': 'Akroma\'s Vengeance', 'multiverseid': 205366, 'number': '1'},
            {'set': 'ARC', 'name': 'All in Good Time', 'multiverseid': 212648, 'number': '1'},
            {'set': 'ARC', 'name': 'Leonin Abunas', 'multiverseid': 220527, 'number': '1'},
            {'set': 'ISD', 'name': 'Delver of Secrets', 'multiverseid': 226749, 'number': '51a'},
            {'set': 'ISD', 'name': 'Insectile Aberration', 'multiverseid': 226755, 'number': '51b'},
            {'set': 'ISD', 'name': 'Abattoir Ghoul', 'multiverseid': 222911, 'number': '85'},
            {'set': 'PC2', 'name': 'Stairs to Infinity', 'multiverseid': 226521, 'number': 'P1'},
            {'set': 'PC2', 'name': 'Chaotic Æther', 'multiverseid': 226509, 'number': '1'},
            {'set': 'PC2', 'name': 'Armored Griffin', 'multiverseid': 271234, 'number': '1'},
            {'set': 'PC2', 'name': 'Akoum', 'multiverseid': 226512, 'number': '9'},
            {'set': 'VMA', 'name': 'Academy Elite', 'multiverseid': 382835, 'number': '55'},
        ]
        self.assertEqual(expected, rows)
