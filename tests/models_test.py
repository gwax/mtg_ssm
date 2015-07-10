"""Tests for mtgcdb.models"""

from mtgcdb import models

from tests import sqlite_testcase


class ModelsTest(sqlite_testcase.SqliteTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_tag_find_or_create_new(self):
        # Execute
        card = models.CardType.find_or_create(self.session, 'Type1')
        self.session.commit()

        # Verify
        db_card = self.session.query(
            models.CardType).filter_by(name='Type1').first()
        self.assertIs(card, db_card)

    def test_tag_find_or_create_existing(self):
        # Setup
        card = models.CardType(name='Type1')
        self.session.add(card)
        self.session.commit()

        # Execute
        new_card = models.CardType.find_or_create(self.session, 'Type1')

        # Verify
        self.assertIs(card, new_card)

    def test_card_same_type_removal(self):
        # Setup
        card1 = models.Card(name='Card1')
        card2 = models.Card(name='Card2')
        type1 = models.CardType(name='Type1')
        type2 = models.CardType(name='Type2')
        card1.types.update([type1, type2])
        card2.types.update([type1, type2])
        self.session.add_all([type1, type2, card1, card2])

        # Execute
        card1.types.remove(type1)

        # Verify
        self.assertEqual({type2}, card1.types)
        self.assertEqual({type1, type2}, card2.types)
