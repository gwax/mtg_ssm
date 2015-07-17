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
        ret_card_set = mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        self.assertIsNotNone(ret_card_set.id)
        [card_set] = self.session.query(models.CardSet).all()
        self.assertIs(ret_card_set, card_set)
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block)
        self.assertEqual([], card_set.printings)

    def test_update_set(self):
        # Setup
        setup_card_set = models.CardSet(id=7, code='ISD', name='Bunk')
        self.session.add(setup_card_set)
        self.session.commit()
        set_data = self.mtg_data['ISD']

        # Execute
        mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        [card_set] = self.session.query(models.CardSet).all()
        self.assertIs(setup_card_set, card_set)
        self.assertEqual(7, card_set.id)
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block)
        self.assertEqual([], card_set.printings)

    def test_online_only(self):
        # Execute
        isd_set = mtgjson.update_set(self.session, self.mtg_data['ISD'])
        vma_set = mtgjson.update_set(self.session, self.mtg_data['VMA'])

        # Verify
        self.assertTrue(vma_set.online_only)
        self.assertFalse(isd_set.online_only)

    def test_create_card(self):
        # Setup
        card_data = self.mtg_data['ISD']['cards'][0]

        # Execute
        ret_card = mtgjson.update_card(self.session, card_data)
        self.session.commit()

        # Verify
        self.assertIsNotNone(ret_card.id)
        [card] = self.session.query(models.Card).all()
        self.assertIs(ret_card, card)
        self.assertEqual('Abattoir Ghoul', card.name)

    def test_update_card(self):
        # Setup
        setup_card = models.Card(id=12, name='Abattoir Ghoul')
        self.session.add(setup_card)
        self.session.commit()
        card_data = self.mtg_data['ISD']['cards'][0]

        # Execute
        mtgjson.update_card(self.session, card_data)
        self.session.commit()

        # Verify
        [card] = self.session.query(models.Card).all()
        self.assertIs(setup_card, card)
        self.assertEqual(12, card.id)
        self.assertEqual('Abattoir Ghoul', card.name)

    def test_create_printing(self):
        # Setup
        card_set = models.CardSet(id=2, code='ISD', name='Innistrad')
        card = models.Card(id=5, name='Abattoir Ghoul')
        self.session.add(card_set)
        self.session.add(card)
        card_data = self.mtg_data['ISD']['cards'][0]

        # Execute
        ret_printing = mtgjson.update_printing(self.session, card_data, 5, 2)
        self.session.commit()

        # Verify
        self.assertIsNotNone(ret_printing.id)
        [printing] = self.session.query(models.CardPrinting).all()
        self.assertIs(ret_printing, printing)
        self.assertEqual('Abattoir Ghoul', printing.card.name)
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('85', printing.set_number)
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('Volkan Baga', printing.artist)

    def test_update_printing(self):
        # Setup
        card_set = models.CardSet(id=2, code='ISD', name='Innistrad')
        card = models.Card(id=5, name='Abattoir Ghoul')
        setup_printing = models.CardPrinting(
            id=19, card_id=5, set_id=2, set_number='85', multiverseid=222911,
            artist='Hokum')
        self.session.add(card_set)
        self.session.add(card)
        self.session.add(setup_printing)
        self.session.commit()
        card_data = self.mtg_data['ISD']['cards'][0]

        # Execute
        mtgjson.update_printing(self.session, card_data, 5, 2)
        self.session.commit()

        # Verify
        [printing] = self.session.query(models.CardPrinting).all()
        self.assertIs(setup_printing, printing)
        self.assertEqual(19, printing.id)
        self.assertEqual('Abattoir Ghoul', printing.card.name)
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('85', printing.set_number)
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('Volkan Baga', printing.artist)

    def test_update_models(self):
        # Execute
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()

        # Verify
        printings = self.session.query(models.CardPrinting).all()
        set_card_mv_number = [
            (p.set.code, p.card.name, p.multiverseid, p.set_number)
            for p in printings]
        expected = [
            ('LEA', 'Air Elemental', 94, None),
            ('LEA', 'Forest', 288, None),
            ('LEA', 'Forest', 289, None),
            ('ICE', 'Forest', 2746, None),
            ('ICE', 'Forest', 2747, None),
            ('ICE', 'Forest', 2748, None),
            ('ICE', 'Snow-Covered Forest', 2749, None),
            ('HML', 'Cemetery Gate', 2913, None),
            ('HML', 'Cemetery Gate', 2914, None),
            ('S00', 'Rhox', None, None),
            ('pMGD', 'Black Sun\'s Zenith', None, '7'),
            ('HOP', 'Academy at Tolaria West', 198073, '1'),
            ('HOP', 'Akroma\'s Vengeance', 205366, '1'),
            ('ARC', 'All in Good Time', 212648, '1'),
            ('ARC', 'Leonin Abunas', 220527, '1'),
            ('ISD', 'Abattoir Ghoul', 222911, '85'),
            ('ISD', 'Delver of Secrets', 226749, '51a'),
            ('ISD', 'Insectile Aberration', 226755, '51b'),
            ('ISD', 'Forest', 245247, '262'),
            ('ISD', 'Forest', 245248, '263'),
            ('ISD', 'Forest', 245246, '264'),
            ('PC2', 'Akoum', 226512, '9'),
            ('PC2', 'Armored Griffin', 271234, '1'),
            ('PC2', 'Chaotic Æther', 226509, '1'),
            ('PC2', 'Stairs to Infinity', 226521, 'P1'),
            ('VMA', 'Academy Elite', 382835, '55'),
        ]
        self.assertCountEqual(expected, set_card_mv_number)
