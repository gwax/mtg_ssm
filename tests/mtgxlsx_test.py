"""Tests for mtgcdb.mtgxlsx"""

import datetime

import openpyxl

from mtgcdb import models
from mtgcdb import mtgjson
from mtgcdb import mtgxlsx

from tests import mtgjson_testcase
from tests import sqlite_testcase


class MtgXlsxTest(
        sqlite_testcase.SqliteTestCase, mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_create_sets_sheet(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()
        card_sets = self.session.query(models.CardSet) \
            .order_by(models.CardSet.release_date).all()
        book = openpyxl.Workbook()
        sheet = book.create_sheet()

        # Execute
        mtgxlsx.create_sets_sheet(sheet, card_sets)

        # Verify
        rows = [[cell.value for cell in row] for row in sheet.rows]
        # pylint: disable=line-too-long
        expected = [
            ['code', 'name', 'release', 'block', 'type', 'cards'],
            ['LEA', 'Limited Edition Alpha', datetime.datetime(1993, 8, 5), None, 'core', 3],
            ['ICE', 'Ice Age', datetime.datetime(1995, 6, 1), 'Ice Age', 'expansion', 4],
            ['HML', 'Homelands', datetime.datetime(1995, 10, 1), None, 'expansion', 2],
            ['S00', 'Starter 2000', datetime.datetime(2000, 4, 1), None, 'starter', 1],
            ['pMGD', 'Magic Game Day', datetime.datetime(2007, 7, 14), None, 'promo', 1],
            ['HOP', 'Planechase', datetime.datetime(2009, 9, 4), None, 'planechase', 2],
            ['ARC', 'Archenemy', datetime.datetime(2010, 6, 18), None, 'archenemy', 2],
            ['ISD', 'Innistrad', datetime.datetime(2011, 9, 30), 'Innistrad', 'expansion', 3],
            ['PC2', 'Planechase 2012 Edition', datetime.datetime(2012, 6, 1), None, 'planechase', 4],
            ['VMA', 'Vintage Masters', datetime.datetime(2014, 6, 16), None, 'masters', 1],
        ]
        # pylint: enable=line-too-long
        self.assertEqual(expected, rows)

    def test_create_cards_sheet(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()
        forest1 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2746).first()
        forest2 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2747).first()
        forest3 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2748).first()
        forest1.counts['copies'] = 1
        forest2.counts['foils'] = 2
        forest3.counts['copies'] = 3
        forest3.counts['foils'] = 4
        self.session.commit()
        ice_age = self.session.query(models.CardSet).filter_by(code='ICE').one()
        book = openpyxl.Workbook()
        sheet = book.create_sheet()

        # Execute
        mtgxlsx.create_cards_sheet(sheet, ice_age)

        # Verify
        rows = [[cell.value for cell in row] for row in sheet.rows]
        expected = [
            ['name', 'multiverseid', 'number', 'artist', 'copies', 'foils'],
            ['Forest', 2746, None, 'Pat Morrissey', 1, None],
            ['Forest', 2747, None, 'Pat Morrissey', None, 2],
            ['Forest', 2748, None, 'Pat Morrissey', 3, 4],
            ['Snow-Covered Forest', 2749, None, 'Pat Morrissey', None, None],
        ]
        self.assertEqual(expected, rows)

    def test_dump_workbook(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()

        # Execute
        book = mtgxlsx.dump_workbook(self.session)

        # Verify
        expected = [
            'Sets',
            'LEA',
            'ICE',
            'HML',
            'S00',
            'pMGD',
            'HOP',
            'ARC',
            'ISD',
            'PC2',
            'VMA',
        ]
        self.assertEqual(expected, book.sheetnames)

    def test_read_worksheet_counts(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()
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
        book = openpyxl.Workbook()
        sheet = book.create_sheet()
        sheet.title = 'ICE'
        sheet_data = [
            ['name', 'multiverseid', 'number', 'artist', 'copies', 'foils'],
            ['Forest', 2746, None, 'Pat Morrissey', 1, None],
            ['Forest', 2747, None, 'Pat Morrissey', None, 2],
            ['Forest', 2748, None, 'Pat Morrissey', 3, 4],
            ['Snow-Covered Forest', 2749, None, 'Pat Morrissey', None, None],
        ]
        for row in sheet_data:
            sheet.append(row)

        # Execute
        mtgxlsx.read_worksheet_counts(self.session, sheet)
        self.session.commit()

        # Verify
        self.assertEqual({'copies': 1}, forest1.counts)
        self.assertEqual({'foils': 2}, forest2.counts)
        self.assertEqual({'copies': 3, 'foils': 4}, forest3.counts)
        self.assertFalse(forest4.counts)

    def test_read_worksheet_counts_skipping(self):
        # Setup
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()
        book = openpyxl.Workbook()
        sheet = book.create_sheet()
        sheet.title = 'garbage'
        sheet.append(['jabberwocky', 'gobbledy', 'goop'])

        # Execute
        mtgxlsx.read_worksheet_counts(self.session, sheet)

        # Verify
        counts = self.session.query(models.CollectionCount).all()
        self.assertFalse(counts)

    def test_read_workbook_counts(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data)
        self.session.commit()
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
        book = openpyxl.Workbook()
        sets_sheet = book.create_sheet()
        sets_sheet.title = 'Sets'
        sets_sheet.append(['jabberwocky', 'gobbledy', 'goop'])

        cards_sheet = book.create_sheet()
        cards_sheet.title = 'ICE'
        sheet_data = [
            ['name', 'multiverseid', 'number', 'artist', 'copies', 'foils'],
            ['Forest', 2746, None, 'Pat Morrissey', 1, None],
            ['Forest', 2747, None, 'Pat Morrissey', None, 2],
            ['Forest', 2748, None, 'Pat Morrissey', 3, 4],
            ['Snow-Covered Forest', 2749, None, 'Pat Morrissey', None, None],
        ]
        for row in sheet_data:
            cards_sheet.append(row)

        # Execute
        mtgxlsx.read_workbook_counts(self.session, book)
        self.session.commit()

        # Verify
        self.assertEqual({'copies': 1}, forest1.counts)
        self.assertEqual({'foils': 2}, forest2.counts)
        self.assertEqual({'copies': 3, 'foils': 4}, forest3.counts)
        self.assertFalse(forest4.counts)
