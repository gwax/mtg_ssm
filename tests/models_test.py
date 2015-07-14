"""Tests for mtgcdb.models"""

import sqlalchemy as sqla
import sqlalchemy.exc as sqlx

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
        with self.assertRaises(KeyError):
            _ = printing.counts['foils']

    def test_counts_write(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        count = models.CollectionCount(
            print_id=1, type=models.CountTypes.copies, count=5)
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        printing.counts['copies'] = 2
        printing.counts['foils'] = 7
        self.session.commit()

        # Verify
        counts = self.session.query(models.CollectionCount).all()
        print_type_count = [(c.print_id, c.type, c.count) for c in counts]
        expected = [
            (1, models.CountTypes.copies, 2),
            (1, models.CountTypes.foils, 7),
        ]
        self.assertCountEqual(expected, print_type_count)

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
        with self.assertRaises(AttributeError):
            printing.counts['invalid'] = 12

    def test_invalid_counts_value(self):
        # Setup
        card_set = models.CardSet(id=1, code='F', name='Foo')
        card = models.Card(id=1, name='Bar')
        printing = models.CardPrinting(
            id=1, card_id=1, set_id=1, set_number='123abc', multiverseid=27,
            artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        with self.assertRaises(sqlx.IntegrityError):
            printing.counts['copies'] = None
            self.session.commit()
        self.session.rollback()

    def test_counts_delete(self):
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

        # Execute
        del printing.counts['copies']
        self.session.commit()

        # Verify
        self.assertEqual({}, printing.counts)
        with self.assertRaises(KeyError):
            _ = printing.counts['copies']
        self.session.rollback()
