"""Tests for mtgcdb.mtgjson"""

import datetime

from mtgcdb import models
from mtgcdb import mtgjson

from tests import mtgjson_testcase
from tests import sqlite_testcase


class MtgjsonTest(
        sqlite_testcase.SqliteTestCase, mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_create_set(self):
        # Setup
        set_data = self.mtg_data['ISD']

        # Execute
        mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        card_set = self.session.query(models.CardSet).filter_by(code='ISD').first()
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block.name)
        self.assertEqual([], card_set.cards)

    def test_update_set(self):
        # Setup
        self.session.add(models.CardSet(code='ISD', name='Bunk'))
        self.session.commit()
        set_data = self.mtg_data['ISD']

        # Execute
        mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        card_set = self.session.query(models.CardSet).filter_by(code='ISD').first()
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block.name)
        self.assertEqual([], card_set.cards)
