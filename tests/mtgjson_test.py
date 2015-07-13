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
        card_set = mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        self.assertEqual('ISD', card_set.code)

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
        card_set = mtgjson.update_set(self.session, set_data)
        self.session.commit()

        # Verify
        self.assertEqual('ISD', card_set.code)

        card_set = self.session.query(models.CardSet).filter_by(code='ISD').first()
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block.name)
        self.assertEqual([], card_set.cards)

    def test_online_only(self):
        # Execute
        isd_set = mtgjson.update_set(self.session, self.mtg_data['ISD'])
        vma_set = mtgjson.update_set(self.session, self.mtg_data['VMA'])

        # Verify
        self.assertTrue(vma_set.online_only)
        self.assertFalse(isd_set.online_only)

    def test_create_card(self):
        # Setup
        card_data = self.mtg_data['ICE']['cards'][-1]

        # Execute
        card = mtgjson.update_card(self.session, card_data)
        self.session.commit()

        # Verify
        self.assertEqual('Snow-Covered Forest', card.name)

        card = self.session.query(
            models.Card).filter_by(name='Snow-Covered Forest').first()
        self.assertEqual('Snow-Covered Forest', card.name)
        self.assertEqual({'Land'}, {t.name for t in card.types})
        self.assertEqual({'Snow', 'Basic'}, {t.name for t in card.supertypes})

    def test_update_card(self):
        # Setup
        setup_card = models.Card(name='Snow-Covered Forest')
        setup_card.supertypes = set()
        card_data = self.mtg_data['ICE']['cards'][-1]

        # Execute
        card = mtgjson.update_card(self.session, card_data)
        self.session.commit()

        # Verify
        self.assertEqual('Snow-Covered Forest', card.name)

        card = self.session.query(
            models.Card).filter_by(name='Snow-Covered Forest').first()
        self.assertEqual('Snow-Covered Forest', card.name)
        self.assertEqual({'Land'}, {t.name for t in card.types})
        self.assertEqual({'Snow', 'Basic'}, {t.name for t in card.supertypes})

    def test_create_printing(self):
        # Setup
        set_data = self.mtg_data['ISD']
        card_data = set_data['cards'][0]
        card_set = mtgjson.update_set(self.session, set_data)
        card = mtgjson.update_card(self.session, card_data)
        self.session.commit()

        # Execute
        printing = mtgjson.update_printing(
            self.session, card_data, card, card_set)
        self.session.commit()

        # Verify
        self.assertEqual(222911, printing.multiverseid)

        printing = self.session.query(
            models.CardPrinting).filter_by(card=card, set=card_set).first()
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('85', printing.set_number)
        self.assertEqual('Volkan Baga', printing.artist.name)

    def test_update_printing(self):
        # Setup
        set_data = self.mtg_data['ISD']
        card_data = set_data['cards'][0]
        card_set = mtgjson.update_set(self.session, set_data)
        card = mtgjson.update_card(self.session, card_data)
        self.session.add(models.CardPrinting(
            card=card, set=card_set, set_number='85', multiverseid=222911,
            artist=None))
        self.session.commit()

        # Execute
        printing = mtgjson.update_printing(
            self.session, card_data, card, card_set)
        self.session.commit()

        # Verify
        self.assertEqual(222911, printing.multiverseid)

        printing = self.session.query(
            models.CardPrinting).filter_by(card=card, set=card_set).first()
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('85', printing.set_number)
        self.assertEqual('Volkan Baga', printing.artist.name)

    def test_update_rhox(self):
        # Setup
        set_data = self.mtg_data['S00']
        card_data = set_data['cards'][0]
        card_set = mtgjson.update_set(self.session, set_data)
        card = mtgjson.update_card(self.session, card_data)
        self.session.add(models.CardPrinting(card=card, set=card_set))
        self.session.commit()

        # Execute
        mtgjson.update_printing(self.session, card_data, card, card_set)
        self.session.commit()

        # Verify
        printings = self.session.query(models.CardPrinting).all()
        self.assertEqual(1, len(printings))
        self.assertEqual('Mark Zug', printings[0].artist.name)

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
            ('PC2', 'Akoum', 226512, '9'),
            ('PC2', 'Armored Griffin', 271234, '1'),
            ('PC2', 'Chaotic Æther', 226509, '1'),
            ('PC2', 'Stairs to Infinity', 226521, 'P1'),
            ('VMA', 'Academy Elite', 382835, '55'),
        ]
        self.assertCountEqual(expected, set_card_mv_number)
