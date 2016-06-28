"""Tests for mtg_ssm.serialization.xlsx."""

import datetime as dt
import os
import tempfile
from unittest import mock

import openpyxl
import pytest

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts
from mtg_ssm.serialization import interface
from mtg_ssm.serialization import xlsx


@pytest.fixture
def cdb(sets_data):
    """card_db fixture for testing."""
    sets_data = {
        k: v for k, v in sets_data.items()
        if k in {'LEA', 'FEM', 'S00', 'ICE', 'HOP'}}
    return card_db.CardDb(sets_data)


def test_create_all_sets(cdb):
    # Setup
    book = openpyxl.Workbook()
    sheet = book.create_sheet()
    # Execute
    xlsx.create_all_sets(sheet, cdb)
    # Verify
    rows = [[cell.value for cell in row] for row in sheet.rows]
    expected = [
        # pylint: disable=line-too-long
        ['code', 'name', 'release', 'block', 'type', 'cards', 'unique', 'playsets', 'count'],
        ['Total', None, None, None, None, '=SUM(F3:F65535)', '=SUM(G3:G65535)', '=SUM(H3:H65535)', '=SUM(I3:I65535)'],
        ['LEA', 'Limited Edition Alpha', dt.datetime(1993, 8, 5), None, 'core', 4, '=COUNTIF(\'LEA\'!A:A,">0")', '=COUNTIF(\'LEA\'!A:A,">=4")', "=SUM('LEA'!A:A)"],
        ['FEM', 'Fallen Empires', dt.datetime(1994, 11, 1), None, 'expansion', 4, '=COUNTIF(\'FEM\'!A:A,">0")', '=COUNTIF(\'FEM\'!A:A,">=4")', "=SUM('FEM'!A:A)"],
        ['ICE', 'Ice Age', dt.datetime(1995, 6, 1), 'Ice Age', 'expansion', 5, '=COUNTIF(\'ICE\'!A:A,">0")', '=COUNTIF(\'ICE\'!A:A,">=4")', "=SUM('ICE'!A:A)"],
        ['S00', 'Starter 2000', dt.datetime(2000, 4, 1), None, 'starter', 1, '=COUNTIF(\'S00\'!A:A,">0")', '=COUNTIF(\'S00\'!A:A,">=4")', "=SUM('S00'!A:A)"],
        ['HOP', 'Planechase', dt.datetime(2009, 9, 4), None, 'planechase', 3, '=COUNTIF(\'HOP\'!A:A,">0")', '=COUNTIF(\'HOP\'!A:A,">=4")', "=SUM('HOP'!A:A)"],
    ]
    assert rows == expected
    assert sheet.title == 'All Sets'


def test_create_haverefs(cdb):
    # Setup
    fem_thallid_ids = [
        '3deebffcf4f5152f4a5cc270cfac746a3bd2089d',
        'bd676ca33f673a6769312e8e9b12e1cf40ae2c84',
        'f68597b2ddfbd715c5c51b94e3a39e0a307e3f40',
        '378e47697b1b74df8c901cac23f7402b01da31b2',
    ]
    fem_thallids = [
        cdb.id_to_printing[pid] for pid in fem_thallid_ids]
    fem_thallids.sort(key=lambda p: p.multiverseid)
    # Execute
    haverefs = xlsx.create_haverefs(fem_thallids)
    # Verify
    expected = "'FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5"
    assert haverefs == expected


@pytest.mark.parametrize('name,exclude_set_codes,expected', [
    ('Forest', (), None),
    ('Rhox', (), '=IF(\'S00\'!A2>0,"S00: "&\'S00\'!A2&", ","")'),
    ('Rhox', ('S00',), None),
    ('Dark Ritual', ('LEA',), '=IF(\'ICE\'!A2>0,"ICE: "&\'ICE\'!A2&", ","")'
                              '&IF(\'HOP\'!A4>0,"HOP: "&\'HOP\'!A4&", ","")'),
    ('Dark Ritual', ('LEA', 'ICE'), '=IF(\'HOP\'!A4>0,"HOP: "'
                                    '&\'HOP\'!A4&", ","")'),
    ('Thallid', (), '=IF(\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5>0,'
                    '"FEM: "&\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5'
                    '&", ","")')
])
def test_get_references(cdb, name, exclude_set_codes, expected):
    card = cdb.name_to_card[name]
    exclude_sets = {
        cdb.code_to_card_set[set_code] for set_code in exclude_set_codes}
    print_refs = xlsx.get_references(card, exclude_sets=exclude_sets)
    assert print_refs == expected


def test_create_all_cards_sheet(cdb):
    # Setup
    book = openpyxl.Workbook()
    sheet = book.create_sheet()

    # Execute
    xlsx.create_all_cards(sheet, cdb)

    # Verify
    rows = [[cell.value for cell in row] for row in sheet.rows]
    expected = [
        # pylint: disable=line-too-long
        ['name', 'have'],
        ['Academy at Tolaria West', '=IF(\'HOP\'!A2>0,"HOP: "&\'HOP\'!A2&", ","")'],
        ['Air Elemental', '=IF(\'LEA\'!A3>0,"LEA: "&\'LEA\'!A3&", ","")'],
        ["Akroma's Vengeance", '=IF(\'HOP\'!A3>0,"HOP: "&\'HOP\'!A3&", ","")'],
        ['Dark Ritual', '=IF(\'LEA\'!A2>0,"LEA: "&\'LEA\'!A2&", ","")&'
                        'IF(\'ICE\'!A2>0,"ICE: "&\'ICE\'!A2&", ","")&'
                        'IF(\'HOP\'!A4>0,"HOP: "&\'HOP\'!A4&", ","")'],
        ['Forest', None],
        ['Rhox', '=IF(\'S00\'!A2>0,"S00: "&\'S00\'!A2&", ","")'],
        ['Snow-Covered Forest', '=IF(\'ICE\'!A6>0,"ICE: "&\'ICE\'!A6&", ","")'],
        ['Thallid', '=IF(\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5>0,"FEM: "&\'FEM\'!A2+\'FEM\'!A3+\'FEM\'!A4+\'FEM\'!A5&", ","")'],
    ]
    assert rows == expected
    assert sheet.title == 'All Cards'


def test_create_set_sheet(cdb):
    # Setup
    forest1 = cdb.id_to_printing[
        '676a1f5b64dc03bbb3876840c3ff2ba2c16f99cb']
    forest2 = cdb.id_to_printing[
        'd0a4414893bc2f9bd3beea2f8f2693635ef926a4']
    forest3 = cdb.id_to_printing[
        'c78d2da78c68c558b1adc734b3f164e885407ffc']
    print_counts = {
        forest1: {counts.CountTypes.copies: 1},
        forest2: {counts.CountTypes.foils: 2},
        forest3: {
            counts.CountTypes.copies: 3,
            counts.CountTypes.foils: 4,
        }
    }

    ice_age = cdb.code_to_card_set['ICE']
    book = openpyxl.Workbook()
    sheet = book.create_sheet()

    # Execute
    xlsx.create_set_sheet(sheet, ice_age, print_counts)

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
    assert rows == expected
    assert sheet.title == 'ICE'


def test_write(cdb):
    # Setup
    print_counts = {
        cdb.id_to_printing['536d407161fa03eddee7da0e823c2042a8fa0262']: {
            counts.CountTypes.copies: 7,
            counts.CountTypes.foils: 12,
        }
    }
    serializer = xlsx.MtgXlsxSerializer(cdb)
    with tempfile.TemporaryDirectory() as tmpdirname:
        xlsxfilename = os.path.join(tmpdirname, 'outfile.xlsx')

        # Execute
        serializer.write(xlsxfilename, print_counts)

        # Verify
        workbook = openpyxl.load_workbook(filename=xlsxfilename)
    expected_sheetnames = [
        'All Sets', 'All Cards', 'LEA', 'FEM', 'ICE', 'S00', 'HOP']
    assert workbook.sheetnames == expected_sheetnames

    s00_rows = [[cell.value for cell in row] for row in workbook['S00']]
    expected = [
        # pylint: disable=line-too-long
        ['have', 'name', 'id', 'multiverseid', 'number', 'artist', 'copies', 'foils', 'others'],
        ['=G2+H2', 'Rhox', '536d407161fa03eddee7da0e823c2042a8fa0262', None, None, 'Mark Zug', 7, 12, None],
    ]
    assert s00_rows == expected


def test_counts_from_sheet():
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
    assert rows == expected


def test_read_bad_set(cdb):
    # Setup
    serializer = xlsx.MtgXlsxSerializer(cdb)
    workbook = openpyxl.Workbook()
    workbook['Sheet'].title = 'BADSET'
    with tempfile.TemporaryDirectory() as tmpdirname:
        xlsxfilename = os.path.join(tmpdirname, 'infile.xlsx')
        workbook.save(xlsxfilename)

        # Execute
        with pytest.raises(interface.DeserializationError):
            serializer.read(xlsxfilename)


def test_read_from_file(cdb):
    # Setup
    serializer = xlsx.MtgXlsxSerializer(cdb)
    workbook = openpyxl.Workbook()
    sheet = workbook['Sheet']
    sheet.title = 'S00'
    sheet.append(['id', 'copies', 'foils'])
    sheet.append(['536d407161fa03eddee7da0e823c2042a8fa0262', 3, 7])
    with tempfile.TemporaryDirectory() as tmpdirname:
        xlsxfilename = os.path.join(tmpdirname, 'infile.xlsx')
        workbook.save(xlsxfilename)

        # Execute
        print_counts = serializer.read(xlsxfilename)

    # Verify
    assert print_counts == {
        cdb.id_to_printing['536d407161fa03eddee7da0e823c2042a8fa0262']: {
            counts.CountTypes.copies: 3,
            counts.CountTypes.foils: 7,
        }
    }
