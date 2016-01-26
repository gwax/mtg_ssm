"""Tests for mtg_ssm.mtgjson"""

import datetime

from mtg_ssm.db import models
from mtg_ssm.mtgjson import mtgjson

from tests.mtgjson import mtgjson_testcase
from tests.db import sqlite_testcase


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
        ret_card_set = mtgjson.create_set(set_data)
        self.session.merge(ret_card_set)
        self.session.commit()

        # Verify
        [card_set] = self.session.query(models.CardSet).all()
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block)
        self.assertEqual([], card_set.printings)

    def test_update_set(self):
        # Setup
        setup_card_set = models.CardSet(code='ISD', name='Bunk')
        self.session.add(setup_card_set)
        self.session.commit()
        set_data = self.mtg_data['ISD']

        # Execute
        ret_card_set = mtgjson.create_set(set_data)
        self.session.merge(ret_card_set)
        self.session.commit()

        # Verify
        [card_set] = self.session.query(models.CardSet).all()
        self.assertEqual('ISD', card_set.code)
        self.assertEqual('Innistrad', card_set.name)
        self.assertEqual(datetime.date(2011, 9, 30), card_set.release_date)
        self.assertEqual('expansion', card_set.type)
        self.assertFalse(card_set.online_only)
        self.assertEqual('Innistrad', card_set.block)
        self.assertEqual([], card_set.printings)

    def test_online_only(self):
        # Execute
        isd_set = mtgjson.create_set(self.mtg_data['ISD'])
        vma_set = mtgjson.create_set(self.mtg_data['VMA'])

        # Verify
        self.assertTrue(vma_set.online_only)
        self.assertFalse(isd_set.online_only)

    def test_create_card(self):
        # Setup
        [card_data] = [
            c for c in self.mtg_data['ISD']['cards']
            if c['id'] == '958ae1416f8f6287115ccd7c5c61f2415a313546']

        # Execute
        ret_card = mtgjson.create_card(card_data)
        self.session.merge(ret_card)
        self.session.commit()

        # Verify
        [card] = self.session.query(models.Card).all()
        self.assertEqual('Abattoir Ghoul', card.name)
        self.assertFalse(card.strict_basic)

    def test_update_card(self):
        # Setup
        setup_card = models.Card(name='Abattoir Ghoul', strict_basic=True)
        self.session.add(setup_card)
        self.session.commit()
        [card_data] = [
            c for c in self.mtg_data['ISD']['cards']
            if c['id'] == '958ae1416f8f6287115ccd7c5c61f2415a313546']

        # Execute
        ret_card = mtgjson.create_card(card_data)
        self.session.merge(ret_card)
        self.session.commit()

        # Verify
        [card] = self.session.query(models.Card).all()
        self.assertEqual('Abattoir Ghoul', card.name)
        self.assertFalse(card.strict_basic)

    def test_strict_basic(self):
        # Execute
        [ag_card_data] = [
            c for c in self.mtg_data['ISD']['cards']
            if c['id'] == '958ae1416f8f6287115ccd7c5c61f2415a313546']
        [f_card_data] = [
            c for c in self.mtg_data['ICE']['cards']
            if c['id'] == '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb']
        ag_card = mtgjson.create_card(ag_card_data)
        f_card = mtgjson.create_card(f_card_data)

        # Verify
        self.assertEqual('Abattoir Ghoul', ag_card.name)
        self.assertFalse(ag_card.strict_basic)
        self.assertEqual('Forest', f_card.name)
        self.assertTrue(f_card.strict_basic)

    def test_create_printing(self):
        # Setup
        card_set = models.CardSet(code='ISD', name='Innistrad')
        card = models.Card(name='Abattoir Ghoul')
        self.session.add(card_set)
        self.session.add(card)
        self.session.flush()
        [card_data] = [
            c for c in self.mtg_data['ISD']['cards']
            if c['id'] == '958ae1416f8f6287115ccd7c5c61f2415a313546']

        # Execute
        ret_printing = mtgjson.create_printing(card_data, 'ISD')
        self.session.merge(ret_printing)
        self.session.commit()

        # Verify
        [printing] = self.session.query(models.CardPrinting).all()
        self.assertEqual(
            '958ae1416f8f6287115ccd7c5c61f2415a313546', printing.id)
        self.assertEqual('Abattoir Ghoul', printing.card.name)
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('85', printing.set_number)
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('Volkan Baga', printing.artist)

    def test_update_printing(self):
        # Setup
        card_set = models.CardSet(code='ISD', name='Innistrad')
        card = models.Card(name='Abattoir Ghoul')
        setup_printing = models.CardPrinting(
            id='958ae1416f8f6287115ccd7c5c61f2415a313546',
            card_name='Abattoir Ghoul', set_code='ISD', artist='Hokum')
        self.session.add(card_set)
        self.session.add(card)
        self.session.add(setup_printing)
        self.session.commit()
        [card_data] = [
            c for c in self.mtg_data['ISD']['cards']
            if c['id'] == '958ae1416f8f6287115ccd7c5c61f2415a313546']

        # Execute
        ret_printing = mtgjson.create_printing(card_data, 'ISD')
        self.session.merge(ret_printing)
        self.session.commit()

        # Verify
        [printing] = self.session.query(models.CardPrinting).all()
        self.assertEqual(
            '958ae1416f8f6287115ccd7c5c61f2415a313546', printing.id)
        self.assertEqual('Abattoir Ghoul', printing.card.name)
        self.assertEqual('ISD', printing.set.code)
        self.assertEqual('85', printing.set_number)
        self.assertEqual(222911, printing.multiverseid)
        self.assertEqual('Volkan Baga', printing.artist)

    def test_update_models_with_online_only(self):
        # Execute
        mtgjson.update_models(self.session, self.mtg_data, True)
        self.session.commit()

        # Verify
        printings = self.session.query(models.CardPrinting).all()
        set_card_mv_number = [
            (p.set.code, p.card.name, p.multiverseid, p.set_number)
            for p in printings]
        expected = [
            ('LEA', 'Dark Ritual', 54, None),
            ('LEA', 'Air Elemental', 94, None),
            ('LEA', 'Forest', 288, None),
            ('LEA', 'Forest', 289, None),
            ('FEM', 'Thallid', 1924, None),
            ('FEM', 'Thallid', 1926, None),
            ('FEM', 'Thallid', 1927, None),
            ('FEM', 'Thallid', 1925, None),
            ('pMEI', 'Arena', 97042, '1'),
            ('ICE', 'Dark Ritual', 2444, None),
            ('ICE', 'Forest', 2746, None),
            ('ICE', 'Forest', 2747, None),
            ('ICE', 'Forest', 2748, None),
            ('ICE', 'Snow-Covered Forest', 2749, None),
            ('HML', 'Cemetery Gate', 2913, None),
            ('HML', 'Cemetery Gate', 2914, None),
            ('S00', 'Rhox', None, None),
            ('PLS', 'Ertai, the Corrupted', 25614, '107'),
            ('PLS', 'Ertai, the Corrupted', 29292, '★107'),
            ('pMGD', 'Black Sun\'s Zenith', None, '7'),
            ('HOP', 'Academy at Tolaria West', 198073, '1'),
            ('HOP', 'Akroma\'s Vengeance', 205366, '1'),
            ('HOP', 'Dark Ritual', 205422, '24'),
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
            ('MMA', 'Thallid', 370352, '167'),
            ('VMA', 'Academy Elite', 382835, '55'),
        ]
        self.assertCountEqual(expected, set_card_mv_number)

    def test_update_models_without_online_only(self):
        # Execute
        mtgjson.update_models(self.session, self.mtg_data, False)
        self.session.commit()

        # Verify
        printings = self.session.query(models.CardPrinting).all()
        set_card_mv_number = [
            (p.set.code, p.card.name, p.multiverseid, p.set_number)
            for p in printings]
        expected = [
            ('LEA', 'Dark Ritual', 54, None),
            ('LEA', 'Air Elemental', 94, None),
            ('LEA', 'Forest', 288, None),
            ('LEA', 'Forest', 289, None),
            ('FEM', 'Thallid', 1924, None),
            ('FEM', 'Thallid', 1926, None),
            ('FEM', 'Thallid', 1927, None),
            ('FEM', 'Thallid', 1925, None),
            ('pMEI', 'Arena', 97042, '1'),
            ('ICE', 'Dark Ritual', 2444, None),
            ('ICE', 'Forest', 2746, None),
            ('ICE', 'Forest', 2747, None),
            ('ICE', 'Forest', 2748, None),
            ('ICE', 'Snow-Covered Forest', 2749, None),
            ('HML', 'Cemetery Gate', 2913, None),
            ('HML', 'Cemetery Gate', 2914, None),
            ('S00', 'Rhox', None, None),
            ('PLS', 'Ertai, the Corrupted', 25614, '107'),
            ('PLS', 'Ertai, the Corrupted', 29292, '★107'),
            ('pMGD', 'Black Sun\'s Zenith', None, '7'),
            ('HOP', 'Academy at Tolaria West', 198073, '1'),
            ('HOP', 'Akroma\'s Vengeance', 205366, '1'),
            ('HOP', 'Dark Ritual', 205422, '24'),
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
            ('MMA', 'Thallid', 370352, '167'),
        ]
        self.assertCountEqual(expected, set_card_mv_number)
