"""Tests for mtg_ssm.serialization.xlsx."""

import datetime as dt
import os
import tempfile
from unittest import mock

import openpyxl

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface
from mtg_ssm.serialization import xlsx

from tests.mtgjson import mtgjson_testcase


class XlsxSerializerTest(mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        self.collection = collection.Collection(self.mtg_data)

    def test_create_all_sets(self):
        # Setup
        book = openpyxl.Workbook()
        sheet = book.create_sheet()
        # Execute
        xlsx.create_all_sets(sheet, self.collection)
        # Verify
        rows = [[cell.value for cell in row] for row in sheet.rows]
        expected = [
            # pylint: disable=line-too-long
            ['code', 'name', 'release', 'block', 'type', 'cards', 'unique', 'playsets', 'count'],
            ['Total', None, None, None, None, '=SUM(F3:F65535)', '=SUM(G3:G65535)', '=SUM(H3:H65535)', '=SUM(I3:I65535)'],
            ['LEA', 'Limited Edition Alpha', dt.datetime(1993, 8, 5), None, 'core', 4, '=COUNTIF(\'LEA\'!A:A,">0")', '=COUNTIF(\'LEA\'!A:A,">=4")', "=SUM('LEA'!A:A)"],
            ['FEM', 'Fallen Empires', dt.datetime(1994, 11, 1), None, 'expansion', 4, '=COUNTIF(\'FEM\'!A:A,">0")', '=COUNTIF(\'FEM\'!A:A,">=4")', "=SUM('FEM'!A:A)"],
            ['pMEI', 'Media Inserts', dt.datetime(1995, 1, 1), None, 'promo', 1, '=COUNTIF(\'pMEI\'!A:A,">0")', '=COUNTIF(\'pMEI\'!A:A,">=4")', "=SUM('pMEI'!A:A)"],
            ['ICE', 'Ice Age', dt.datetime(1995, 6, 1), 'Ice Age', 'expansion', 5, '=COUNTIF(\'ICE\'!A:A,">0")', '=COUNTIF(\'ICE\'!A:A,">=4")', "=SUM('ICE'!A:A)"],
            ['HML', 'Homelands', dt.datetime(1995, 10, 1), None, 'expansion', 2, '=COUNTIF(\'HML\'!A:A,">0")', '=COUNTIF(\'HML\'!A:A,">=4")', "=SUM('HML'!A:A)"],
            ['S00', 'Starter 2000', dt.datetime(2000, 4, 1), None, 'starter', 1, '=COUNTIF(\'S00\'!A:A,">0")', '=COUNTIF(\'S00\'!A:A,">=4")', "=SUM('S00'!A:A)"],
            ['PLS', 'Planeshift', dt.datetime(2001, 2, 5), 'Invasion', 'expansion', 2, '=COUNTIF(\'PLS\'!A:A,">0")', '=COUNTIF(\'PLS\'!A:A,">=4")', "=SUM('PLS'!A:A)"],
            ['CHK', 'Champions of Kamigawa', dt.datetime(2004, 10, 1, 0, 0), 'Kamigawa', 'expansion', 2, '=COUNTIF(\'CHK\'!A:A,">0")', '=COUNTIF(\'CHK\'!A:A,">=4")', "=SUM('CHK'!A:A)"],
            ['PLC', 'Planar Chaos', dt.datetime(2007, 2, 2, 0, 0), 'Time Spiral', 'expansion', 2, '=COUNTIF(\'PLC\'!A:A,">0")', '=COUNTIF(\'PLC\'!A:A,">=4")', "=SUM('PLC'!A:A)"],
            ['pMGD', 'Magic Game Day', dt.datetime(2007, 7, 14), None, 'promo', 1, '=COUNTIF(\'pMGD\'!A:A,">0")', '=COUNTIF(\'pMGD\'!A:A,">=4")', "=SUM('pMGD'!A:A)"],
            ['HOP', 'Planechase', dt.datetime(2009, 9, 4), None, 'planechase', 3, '=COUNTIF(\'HOP\'!A:A,">0")', '=COUNTIF(\'HOP\'!A:A,">=4")', "=SUM('HOP'!A:A)"],
            ['ARC', 'Archenemy', dt.datetime(2010, 6, 18), None, 'archenemy', 2, '=COUNTIF(\'ARC\'!A:A,">0")', '=COUNTIF(\'ARC\'!A:A,">=4")', "=SUM('ARC'!A:A)"],
            ['ISD', 'Innistrad', dt.datetime(2011, 9, 30), 'Innistrad', 'expansion', 6, '=COUNTIF(\'ISD\'!A:A,">0")', '=COUNTIF(\'ISD\'!A:A,">=4")', "=SUM('ISD'!A:A)"],
            ['PC2', 'Planechase 2012 Edition', dt.datetime(2012, 6, 1), None, 'planechase', 4, '=COUNTIF(\'PC2\'!A:A,">0")', '=COUNTIF(\'PC2\'!A:A,">=4")', "=SUM('PC2'!A:A)"],
            ['MMA', 'Modern Masters', dt.datetime(2013, 6, 7, 0, 0), None, 'reprint', 1, '=COUNTIF(\'MMA\'!A:A,">0")', '=COUNTIF(\'MMA\'!A:A,">=4")', "=SUM('MMA'!A:A)"],
            ['OGW', 'Oath of the Gatewatch', dt.datetime(2016, 1, 22, 0, 0), 'Battle for Zendikar', 'expansion', 4, '=COUNTIF(\'OGW\'!A:A,">0")', '=COUNTIF(\'OGW\'!A:A,">=4")', "=SUM('OGW'!A:A)"],
        ]
        self.assertEqual(expected, rows)
        self.assertEqual('All Sets', sheet.title)

    def test_create_haverefs(self):
        # Setup
        fem_thallid_ids = [
            '3deebffcf4f5152f4a5cc270cfac746a3bd2089d',
            'bd676ca33f673a6769312e8e9b12e1cf40ae2c84',
            'f68597b2ddfbd715c5c51b94e3a39e0a307e3f40',
            '378e47697b1b74df8c901cac23f7402b01da31b2',
        ]
        fem_thallids = [
            self.collection.id_to_printing[pid] for pid in fem_thallid_ids]
        fem_thallids.sort(key=lambda p: p.multiverseid)
        # Execute
        haverefs = xlsx.create_haverefs(fem_thallids)
        # Verify
        expected = "'FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5"
        self.assertEqual(expected, haverefs)

    def test_get_refs_basic_land(self):
        # Setup
        forest = self.collection.name_to_card['Forest']
        # Execute
        print_refs = xlsx.get_references(forest)
        # Verify
        self.assertIsNone(print_refs)

    def test_get_refs_singular(self):
        # Setup
        rhox = self.collection.name_to_card['Rhox']
        # Execute
        print_refs = xlsx.get_references(rhox)
        # Verify
        expected = '=IF(\'S00\'!A2>0,"S00: "&\'S00\'!A2&", ","")'
        self.assertEqual(expected, print_refs)

    def test_get_refs_exclude_only(self):
        # Setup
        rhox = self.collection.name_to_card['Rhox']
        s00 = self.collection.code_to_card_set['S00']
        # Execute
        print_refs = xlsx.get_references(rhox, exclude_sets={s00})
        # Verify'
        self.assertFalse(print_refs)

    def test_get_refs_multiple_sets(self):
        # Setup
        dark_rit = self.collection.name_to_card['Dark Ritual']
        lea = self.collection.code_to_card_set['LEA']
        # Execute
        print_refs = xlsx.get_references(dark_rit, exclude_sets={lea})
        # Verify
        expected = (
            '=IF(\'ICE\'!A2>0,"ICE: "&\'ICE\'!A2&", ","")'
            '&IF(\'HOP\'!A4>0,"HOP: "&\'HOP\'!A4&", ","")')
        self.assertEqual(expected, print_refs)

    def test_get_refs_exclude_multiple(self):
        # Setup
        dark_rit = self.collection.name_to_card['Dark Ritual']
        lea = self.collection.code_to_card_set['LEA']
        ice = self.collection.code_to_card_set['ICE']
        # Execute
        print_refs = xlsx.get_references(dark_rit, exclude_sets={lea, ice})
        # Verify
        expected = '=IF(\'HOP\'!A4>0,"HOP: "&\'HOP\'!A4&", ","")'
        self.assertEqual(expected, print_refs)

    def test_get_refs_multiple_variants(self):
        # Setup
        thallid = self.collection.name_to_card['Thallid']
        mma = self.collection.code_to_card_set['MMA']
        # Execute
        print_refs = xlsx.get_references(thallid, exclude_sets={mma})
        # Verify
        expected = (
            '=IF(\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5>0,'
            '"FEM: "&\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5&", ","")')
        self.assertEqual(expected, print_refs)

    def test_create_set_sheet(self):
        # Setup
        forest1 = self.collection.id_to_printing[
            '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb']
        forest2 = self.collection.id_to_printing[
            'd0a4414893bc2f9bd3beea2f8f2693635ef926a4']
        forest3 = self.collection.id_to_printing[
            'c78d2da78c68c558b1adc734b3f164e885407ffc']
        forest1.counts[models.CountTypes.copies] = 1
        forest2.counts[models.CountTypes.foils] = 2
        forest3.counts[models.CountTypes.copies] = 3
        forest3.counts[models.CountTypes.foils] = 4

        ice_age = self.collection.code_to_card_set['ICE']
        book = openpyxl.Workbook()
        sheet = book.create_sheet()

        # Execute
        xlsx.create_set_sheet(sheet, ice_age)

        # Verify
        rows = [[cell.value for cell in row] for row in sheet.rows]
        expected = [
            # pylint: disable=line-too-long
            ['have', 'name', 'id', 'multiverseid', 'number', 'artist', 'copies', 'foils', 'others'],
            ['=G2+H2', 'Dark Ritual', '2fab0ea29e3bbe8bfbc981a4c8163f3e7d267853', 2444, None, 'Justin Hampton', None, None, mock.ANY],
            ['=G3+H3', 'Forest', '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb', 2746, None, 'Pat Morrissey', 1, None, mock.ANY],
            ['=G4+H4', 'Forest', 'd0a4414893bc2f9bd3beea2f8f2693635ef926a4', 2747, None, 'Pat Morrissey', None, 2, mock.ANY],
            ['=G5+H5', 'Forest', 'c78d2da78c68c558b1adc734b3f164e885407ffc', 2748, None, 'Pat Morrissey', 3, 4, mock.ANY],
            ['=G6+H6', 'Snow-Covered Forest', '5e9f08498a9343b1954103e493da2586be0fe394', 2749, None, 'Pat Morrissey', None, None, mock.ANY],
        ]
        self.assertEqual(expected, rows)
        self.assertEqual('ICE', sheet.title)

    def test_write_to_file(self):
        # Setup
        printing = self.collection.id_to_printing[
            '536d407161fa03eddee7da0e823c2042a8fa0262']
        printing.counts[models.CountTypes.copies] = 7
        printing.counts[models.CountTypes.foils] = 12
        serializer = xlsx.MtgXlsxSerializer(self.collection)
        with tempfile.TemporaryDirectory() as tmpdirname:
            xlsxfilename = os.path.join(tmpdirname, 'outfile.xlsx')

            # Execute
            serializer.write_to_file(xlsxfilename)

            # Verify
            workbook = openpyxl.load_workbook(filename=xlsxfilename)
        expected_sheetnames = [
            'All Sets',
            'LEA',
            'FEM',
            'pMEI',
            'ICE',
            'HML',
            'S00',
            'PLS',
            'CHK',
            'PLC',
            'pMGD',
            'HOP',
            'ARC',
            'ISD',
            'PC2',
            'MMA',
            'OGW',
        ]
        self.assertEqual(expected_sheetnames, workbook.sheetnames)

        s00_rows = [[cell.value for cell in row] for row in workbook['S00']]
        expected = [
            # pylint: disable=line-too-long
            ['have', 'name', 'id', 'multiverseid', 'number', 'artist', 'copies', 'foils', 'others'],
            ['=G2+H2', 'Rhox', '536d407161fa03eddee7da0e823c2042a8fa0262', None, None, 'Mark Zug', 7, 12, None],
        ]
        self.assertEqual(expected, s00_rows)

    def test_counts_from_sheet(self):
        # Setup
        workbook = openpyxl.Workbook()
        sheet = workbook['Sheet']
        sheet.append(['A', 'B', 'C'])
        sheet.append([1, 'B', '=5+7'])
        # Execute
        row_generator = xlsx.counts_from_sheet(sheet)
        # Verify
        rows = list(row_generator)
        expected = [
            {'A': 1, 'B': 'B', 'C': '=5+7'},
        ]
        self.assertEqual(expected, rows)

    def test_read_from_file_bad_set(self):
        # Setup
        serializer = xlsx.MtgXlsxSerializer(self.collection)
        workbook = openpyxl.Workbook()
        workbook['Sheet'].title = 'BADSET'
        with tempfile.TemporaryDirectory() as tmpdirname:
            xlsxfilename = os.path.join(tmpdirname, 'infile.xlsx')
            workbook.save(xlsxfilename)

            # Execute
            with self.assertRaises(interface.DeserializationError):
                serializer.read_from_file(xlsxfilename)

    def test_read_from_file(self):
        # Setup
        serializer = xlsx.MtgXlsxSerializer(self.collection)
        workbook = openpyxl.Workbook()
        sheet = workbook['Sheet']
        sheet.title = 'S00'
        sheet.append(['id', 'copies', 'foils'])
        sheet.append(['536d407161fa03eddee7da0e823c2042a8fa0262', 3, 7])
        with tempfile.TemporaryDirectory() as tmpdirname:
            xlsxfilename = os.path.join(tmpdirname, 'infile.xlsx')
            workbook.save(xlsxfilename)

            # Execute
            serializer.read_from_file(xlsxfilename)

        # Verify
        printing = self.collection.id_to_printing[
            '536d407161fa03eddee7da0e823c2042a8fa0262']
        expected = {models.CountTypes.copies: 3, models.CountTypes.foils: 7}
        self.assertEqual(expected, printing.counts)
