"""Tests for mtg_ssm.mtgcsv"""

from mtg_ssm.db import models
from mtg_ssm.mtgjson import mtgjson
from mtg_ssm.serialization import mtgcsv

from tests.mtgjson import mtgjson_testcase
from tests.db import sqlite_testcase


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
        expected = [
            'set', 'name', 'number', 'multiverseid', 'mtgjid', 'copies',
            'foils']
        self.assertEqual(expected, header)

    def test_dump_rows(self):
        # Setup
        mtg_data = {
            k: v for k, v in self.mtg_data.items()
            if k in ['ICE', 'S00', 'MMA']}
        mtgjson.update_models(self.session, mtg_data, False)
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
            {'set': 'ICE', 'name': 'Dark Ritual', 'multiverseid': 2444, 'mtgjid': '2fab0ea29e3bbe8bfbc981a4c8163f3e7d267853', 'number': None},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2746, 'mtgjid': '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb', 'number': None, 'copies': 1},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2747, 'mtgjid': 'd0a4414893bc2f9bd3beea2f8f2693635ef926a4', 'number': None, 'foils': 2},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2748, 'mtgjid': 'c78d2da78c68c558b1adc734b3f164e885407ffc', 'number': None, 'copies': 3, 'foils': 4},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': 2749, 'mtgjid': '5e9f08498a9343b1954103e493da2586be0fe394', 'number': None},
            {'set': 'S00', 'name': 'Rhox', 'multiverseid': None, 'mtgjid': '536d407161fa03eddee7da0e823c2042a8fa0262', 'number': None},
            {'set': 'MMA', 'name': 'Thallid', 'multiverseid': 370352, 'mtgjid': 'fc46a4b72d216117a352f59217a84d0baeaaacb7', 'number': '167'},
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
            {'set': 'FOO', 'name': 'Thing', 'multiverseid': '27', 'number': '52a', 'copies': '1', 'mtgjid': 'ABC'},
            {'set': 'BAR', 'name': 'Another Thing', 'multiverseid': '', 'number': '57', 'foils': '0', 'copies': '', 'mtgjid': 'DEF'},
        ]
        # pylint: enable=line-too-long

        # Execute
        card_dicts = [mtgcsv.process_row_dict(r) for r in rows]

        # Verify
        # pylint: disable=line-too-long
        expected = [
            {'set': 'FOO', 'name': 'Thing', 'multiverseid': 27, 'number': '52a', 'id': 'ABC', 'copies': 1},
            {'set': 'BAR', 'name': 'Another Thing', 'multiverseid': None, 'number': '57', 'id': 'DEF', 'foils': 0, 'copies': None},
        ]
        # pylint: disable=line-too-long
        self.assertEqual(expected, card_dicts)

    def test_read_row_counts(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data, False)
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
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2746', 'mtgjid': '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb', 'number': '', 'copies': '1'},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2747', 'mtgjid': 'd0a4414893bc2f9bd3beea2f8f2693635ef926a4', 'number': '', 'foils': '2'},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': '2748', 'mtgjid': 'c78d2da78c68c558b1adc734b3f164e885407ffc', 'number': '', 'copies': '3', 'foils': '4'},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': '2749', 'mtgjid': '5e9f08498a9343b1954103e493da2586be0fe394', 'number': '', 'copies': '', 'foils': ''},
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
