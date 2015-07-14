"""Tests for mtgcdb.models"""

import sqlalchemy as sqla

from mtgcdb import models

from tests import sqlite_testcase

class MtgjsonTest(sqlite_testcase.SqliteTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_set_integer_variant(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Verify
        self.assertEqual('123abc', printing.set_number)
        self.assertEqual(123, printing.set_integer)
        self.assertEqual('abc', printing.set_variant)

    def test_set_integer_variant_null(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=2, card_id=1, set_id=1, set_number=None, multiverseid=None,
            artist='Mux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Verify
        self.assertEqual(None, printing.set_number)
        self.assertEqual(None, printing.set_integer)
        self.assertEqual(None, printing.set_variant)

    def test_counts_read(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        count = models.CollectionCount(
            print_id=1, type=models.CountTypes.copies, count=5)
        self.session.add_all([card_set, card, printing, count])
        self.session.commit()

        # Verify
        self.assertEqual(5, printing._counts['copies'].count)
        self.assertEqual(5, printing.counts['copies'])

    def test_counts_write(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        printing.counts['foils'] = 7
        self.session.commit()

        # Verify
        [count] = self.session.query(models.CollectionCount).all()
        self.assertEqual(1, count.print_id)
        self.assertEqual(models.CountTypes.foils, count.type)
        self.assertEqual(7, count.count)

    def test_invalid_counts_key(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        with self.assertRaises(ValueError):
            printing.counts['invalid'] = 12
