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

    def test_get_header(self):
        # Execute
        header = mtgcsv.header()

        # Verify
        expected = ['set', 'name', 'number', 'multiverseid', 'copies', 'foils']
        self.assertEqual(expected, header)

    def test_dump_rows(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data, True)
        self.session.commit()
        forest1 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2746).first()
        forest2 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2747).first()
        forest3 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2748).first()
        forest1.counts['copies'] = 1
        forest2.counts['foils'] = 2
        forest3.counts['copies'] = 3
        forest3.counts['foils'] = 4
        self.session.commit()

        # Execute
        rows = list(mtgcsv.dump_rows(self.session))

        # Verify
        # pylint: disable=line-too-long
        expected = [
            {'set': 'LEA', 'name': 'Dark Ritual', 'multiverseid': 54, 'number': None},
            {'set': 'LEA', 'name': 'Air Elemental', 'multiverseid': 94, 'number': None},
            {'set': 'LEA', 'name': 'Forest', 'multiverseid': 288, 'number': None},
            {'set': 'LEA', 'name': 'Forest', 'multiverseid': 289, 'number': None},
            {'set': 'ICE', 'name': 'Dark Ritual', 'multiverseid': 2444, 'number': None},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2746, 'number': None, 'copies': 1},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2747, 'number': None, 'foils': 2},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2748, 'number': None, 'copies': 3, 'foils': 4},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': 2749, 'number': None},
            {'set': 'HML', 'name': 'Cemetery Gate', 'multiverseid': 2913, 'number': None},
            {'set': 'HML', 'name': 'Cemetery Gate', 'multiverseid': 2914, 'number': None},
            {'set': 'S00', 'name': 'Rhox', 'multiverseid': None, 'number': None},
            {'set': 'pMGD', 'name': 'Black Sun\'s Zenith', 'multiverseid': None, 'number': '7'},
            {'set': 'HOP', 'name': 'Academy at Tolaria West', 'multiverseid': 198073, 'number': '1'},
            {'set': 'HOP', 'name': 'Akroma\'s Vengeance', 'multiverseid': 205366, 'number': '1'},
            {'set': 'HOP', 'name': 'Dark Ritual', 'multiverseid': 205422, 'number': '24'},
            {'set': 'ARC', 'name': 'All in Good Time', 'multiverseid': 212648, 'number': '1'},
            {'set': 'ARC', 'name': 'Leonin Abunas', 'multiverseid': 220527, 'number': '1'},
            {'set': 'ISD', 'name': 'Delver of Secrets', 'multiverseid': 226749, 'number': '51a'},
            {'set': 'ISD', 'name': 'Insectile Aberration', 'multiverseid': 226755, 'number': '51b'},
            {'set': 'ISD', 'name': 'Abattoir Ghoul', 'multiverseid': 222911, 'number': '85'},
            {'set': 'ISD', 'name': 'Forest', 'multiverseid': 245247, 'number': '262'},
            {'set': 'ISD', 'name': 'Forest', 'multiverseid': 245248, 'number': '263'},
            {'set': 'ISD', 'name': 'Forest', 'multiverseid': 245246, 'number': '264'},
            {'set': 'PC2', 'name': 'Stairs to Infinity', 'multiverseid': 226521, 'number': 'P1'},
            {'set': 'PC2', 'name': 'Chaotic Æther', 'multiverseid': 226509, 'number': '1'},
            {'set': 'PC2', 'name': 'Armored Griffin', 'multiverseid': 271234, 'number': '1'},
            {'set': 'PC2', 'name': 'Akoum', 'multiverseid': 226512, 'number': '9'},
            {'set': 'VMA', 'name': 'Academy Elite', 'multiverseid': 382835, 'number': '55'},
        ]
        # pylint: enable=line-too-long
        self.assertEqual(expected, rows)

    def test_int_or_none(self):
        self.assertEqual(None, mtgcsv.int_or_none(None))
        self.assertEqual(None, mtgcsv.int_or_none(''))
        self.assertEqual(1, mtgcsv.int_or_none('1'))
        self.assertEqual(1, mtgcsv.int_or_none(1))
        self.assertEqual(0, mtgcsv.int_or_none('0'))
        self.assertEqual(0, mtgcsv.int_or_none(0))

    def test_process_row_dict(self):
        # Setup
        # pylint: disable=line-too-long
        rows = [
            {'set': 'FOO', 'name': 'Thing', 'multiverseid': '27', 'number': '52a', 'copies': '1'},
            {'set': 'BAR', 'name': 'Another Thing', 'multiverseid': '', 'number': '57', 'foils': '0', 'copies': ''},
        ]
        # pylint: enable=line-too-long

        # Execute
        card_dicts = [mtgcsv.process_row_dict(r) for r in rows]

        # Verify
        # pylint: disable=line-too-long
        expected = [
            {'set': 'FOO', 'name': 'Thing', 'multiverseid': 27, 'number': '52a', 'copies': 1},
            {'set': 'BAR', 'name': 'Another Thing', 'multiverseid': None, 'number': '57', 'foils': 0, 'copies': None},
        ]
        # pylint: disable=line-too-long
        self.assertEqual(expected, card_dicts)

    def test_read_row_counts(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data, True)
        self.session.commit()
        forest1 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2746).first()
        forest2 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2747).first()
        forest3 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2748).first()
        forest4 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2749).first()
        forest4.counts['copies'] = 2
        forest4.counts['foils'] = 3
        self.session.commit()
        # pylint: disable=line-too-long
        rows = [
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2746', 'number': '', 'copies': '1'},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2747', 'number': '', 'foils': '2'},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2748', 'number': '', 'copies': '3', 'foils': '4'},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': '2749', 'number': '', 'copies': '', 'foils': ''},
        ]
        # pylint: enable=line-too-long

        # Execute
        mtgcsv.read_row_counts(self.session, rows)
        self.session.commit()

        # Verify
        self.assertEqual({'copies': 1}, forest1.counts)
        self.assertEqual({'foils': 2}, forest2.counts)
        self.assertEqual({'copies': 3, 'foils': 4}, forest3.counts)
        self.assertFalse(forest4.counts)
