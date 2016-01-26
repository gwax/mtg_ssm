"""Tests for mtg_ssm.models"""

import sqlalchemy.exc as sqlx

from mtg_ssm.db import models

from tests.db import sqlite_testcase


class ModelsTest(sqlite_testcase.SqliteTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_set_integer_variant(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Verify
        self.assertEqual('123abc', printing.set_number)
        self.assertEqual(123, printing.set_integer)
        self.assertEqual('abc', printing.set_variant)

    def test_set_integer_variant_null(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number=None,
            multiverseid=None, artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Verify
        self.assertEqual(None, printing.set_number)
        self.assertEqual(None, printing.set_integer)
        self.assertEqual(None, printing.set_variant)

    def test_set_integer_variant_nonascii_prefix(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='★107',
            multiverseid=27, artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Verify
        self.assertEqual('★107', printing.set_number)
        self.assertEqual(107, printing.set_integer)
        self.assertEqual('★', printing.set_variant)

    def test_counts_read(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        count = models.CollectionCount(
            print_id='A', type=models.CountTypes.copies, count=5)
        self.session.add_all([card_set, card, printing, count])
        self.session.commit()

        # Verify
        self.assertEqual(5, printing.collection_counts['copies'].count)
        self.assertEqual(5, printing.counts['copies'])
        with self.assertRaises(KeyError):
            _ = printing.counts['foils']

    def test_counts_write(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        count = models.CollectionCount(
            print_id='A', type=models.CountTypes.copies, count=5)
        self.session.add_all([card_set, card, printing, count])
        self.session.commit()

        # Execute
        printing.counts['copies'] = 2
        printing.counts['foils'] = 7
        self.session.commit()

        # Verify
        counts = self.session.query(models.CollectionCount).all()
        print_type_count = [(c.print_id, c.type, c.count) for c in counts]
        expected = [
            ('A', models.CountTypes.copies, 2),
            ('A', models.CountTypes.foils, 7),
        ]
        self.assertCountEqual(expected, print_type_count)

    def test_invalid_counts_key(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        with self.assertRaises(AttributeError):
            printing.counts['invalid'] = 12

    def test_invalid_counts_value(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        self.session.add_all([card_set, card, printing])
        self.session.commit()

        # Execute
        with self.assertRaises(sqlx.IntegrityError):
            printing.counts['copies'] = None
            self.session.commit()

    def test_counts_delete(self):
        # Setup
        card_set = models.CardSet(code='F', name='Foo')
        card = models.Card(name='Bar')
        printing = models.CardPrinting(
            id='A', card_name='Bar', set_code='F', set_number='123abc',
            multiverseid=27, artist='Quux')
        count = models.CollectionCount(
            print_id='A', type=models.CountTypes.copies, count=5)
        self.session.add_all([card_set, card, printing, count])
        self.session.commit()

        # Execute
        del printing.counts['copies']
        self.session.commit()

        # Verify
        self.assertEqual({}, printing.counts)
        with self.assertRaises(KeyError):
            _ = printing.counts['copies']
