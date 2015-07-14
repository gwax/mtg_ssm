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
        card_set = models.CardSet(code='A', name='A')
        self.session.add(card_set)
        self.session.flush()
        card = models.Card(
            set_id=card_set.id, name='Foo', set_number='123abc', artist='Me')
        self.session.add(card)
        self.session.commit()

        [card] = self.session.query(models.Card).all()
        self.assertEqual('123abc', card.set_number)
        self.assertEqual(123, card.set_integer)
        self.assertEqual('abc', card.set_variant)
