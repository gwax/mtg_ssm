"""Tests for mtgcdb.mtgcsv"""

from mtgcdb import models
from mtgcdb import mtgdict
from mtgcdb import mtgjson

from tests import mtgjson_testcase
from tests import sqlite_testcase


class MtgDictTest(
        sqlite_testcase.SqliteTestCase, mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

        mtgjson.update_models(self.session, self.mtg_data, False)
        self.session.commit()

    def test_find_printings_by_id(self):
        # Execute
        printing = mtgdict.find_printing(
            self.session, {
                'id': 'e9abef8533c9ce6549147232c5fceff75ffb460a',
            })

        # Verify
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('Forest', printing.card.name)
        self.assertEqual('James Paick', printing.artist)

    def test_find_printing_by_set_and_name(self):
        # Execute
        printing = mtgdict.find_printing(
            self.session, {
                'name': 'Abattoir Ghoul',
                'set': 'ISD',
            })

        # Verify
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('Abattoir Ghoul', printing.card.name)
        self.assertEqual('Volkan Baga', printing.artist)

    def test_find_printing_multiple_set_and_name(self):
        # Execute
        printing = mtgdict.find_printing(
            self.session, {
                'name': 'Forest',
                'set': 'ISD',
            })

        # Verify
        self.assertIsNone(printing)

    def test_find_printing_set_name_number(self):
        # Execute
        printing = mtgdict.find_printing(
            self.session, {
                'name': 'Forest',
                'set': 'ISD',
                'number': '262',
            })

        # Verify
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('Forest', printing.card.name)
        self.assertEqual('James Paick', printing.artist)

    def test_find_printing_set_name_mvid(self):
        # Execute
        printing = mtgdict.find_printing(
            self.session, {
                'name': 'Forest',
                'set': 'ISD',
                'multiverseid': 245247
            })

        # Verify
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('Forest', printing.card.name)
        self.assertEqual('James Paick', printing.artist)

    def test_load_counts(self):
        # Setup
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
        card_dicts = [
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2746, 'number': None, 'copies': 1},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2747, 'number': None, 'foils': 2},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2748, 'number': None, 'copies': 3, 'foils': 4},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': 2749, 'number': None, 'copies': None, 'foils': None},
        ]
        # pylint: enable=line-too-long

        # Execute
        mtgdict.load_counts(self.session, card_dicts)
        self.session.commit()

        # Verify
        self.assertEqual({'copies': 1}, forest1.counts)
        self.assertEqual({'foils': 2}, forest2.counts)
        self.assertEqual({'copies': 3, 'foils': 4}, forest3.counts)
        self.assertFalse(forest4.counts)
