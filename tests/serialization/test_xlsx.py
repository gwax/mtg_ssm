"""Tests for mtg_ssm.serialization.xlsx."""
# pylint: disable=redefined-outer-name

import datetime as dt
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from unittest import mock
from uuid import UUID

import openpyxl
import pytest

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.counts import CountType
from mtg_ssm.containers.counts import ScryfallCardCount
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.serialization import xlsx


@pytest.fixture(scope="session")
def oracle(scryfall_data: ScryfallDataSet) -> Oracle:
    """Oracle fixture."""
    accepted_sets = {"lea", "fem", "s00", "ice", "hop"}
    scryfall_data2 = ScryfallDataSet(
        sets=[s for s in scryfall_data.sets if s.code in accepted_sets],
        cards=[c for c in scryfall_data.cards if c.set in accepted_sets],
    )
    return Oracle(scryfall_data2)


def test_create_all_sets(oracle: Oracle) -> None:
    book = openpyxl.Workbook()
    sheet = book.create_sheet()
    xlsx.create_all_sets(sheet, oracle.index)
    assert sheet.title == "All Sets"
    rows = [[cell.value for cell in row] for row in sheet.rows]
    assert rows == [
        [
            "code",
            "name",
            "release",
            "block",
            "type",
            "cards",
            "unique",
            "playsets",
            "count",
        ],
        [
            "Total",
            None,
            None,
            None,
            None,
            "=SUM(F3:F65535)",
            "=SUM(G3:G65535)",
            "=SUM(H3:H65535)",
            "=SUM(I3:I65535)",
        ],
        [
            "LEA",
            "Limited Edition Alpha",
            dt.date(1993, 8, 5),
            None,
            "core",
            4,
            "=COUNTIF('LEA'!A:A,\">0\")",
            "=COUNTIF('LEA'!A:A,\">=4\")",
            "=SUM('LEA'!A:A)",
        ],
        [
            "FEM",
            "Fallen Empires",
            dt.date(1994, 11, 1),
            None,
            "expansion",
            4,
            "=COUNTIF('FEM'!A:A,\">0\")",
            "=COUNTIF('FEM'!A:A,\">=4\")",
            "=SUM('FEM'!A:A)",
        ],
        [
            "ICE",
            "Ice Age",
            dt.date(1995, 6, 1),
            "Ice Age",
            "expansion",
            5,
            "=COUNTIF('ICE'!A:A,\">0\")",
            "=COUNTIF('ICE'!A:A,\">=4\")",
            "=SUM('ICE'!A:A)",
        ],
        [
            "S00",
            "Starter 2000",
            dt.date(2000, 4, 1),
            None,
            "starter",
            1,
            "=COUNTIF('S00'!A:A,\">0\")",
            "=COUNTIF('S00'!A:A,\">=4\")",
            "=SUM('S00'!A:A)",
        ],
        [
            "HOP",
            "Planechase",
            dt.date(2009, 9, 4),
            None,
            "planechase",
            2,
            "=COUNTIF('HOP'!A:A,\">0\")",
            "=COUNTIF('HOP'!A:A,\">=4\")",
            "=SUM('HOP'!A:A)",
        ],
    ]


def test_create_haverefs(oracle: Oracle) -> None:
    fem_thallids = [c for c in oracle.index.name_to_cards["Thallid"] if c.set == "fem"]
    fem_thallids.sort(key=lambda c: c.collector_number)
    haverefs = xlsx.create_haverefs(oracle.index, fem_thallids)
    assert haverefs == "'FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5"


@pytest.mark.parametrize(
    "name, exclude_sets, expected",
    [
        ("Forest", None, None),
        ("Rhox", None, '=IF(\'S00\'!A2>0,"S00: "&\'S00\'!A2&", ","")'),
        ("Rhox", {"s00"}, None),
        (
            "Dark Ritual",
            {"lea"},
            '=IF(\'ICE\'!A2>0,"ICE: "&\'ICE\'!A2&", ","")&IF(\'HOP\'!A3>0,"HOP: "&\'HOP\'!A3&", ","")',
        ),
        ("Dark Ritual", {"lea", "ice"}, '=IF(\'HOP\'!A3>0,"HOP: "&\'HOP\'!A3&", ","")'),
        (
            "Thallid",
            None,
            "=IF('FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5>0,\"FEM: \"&'FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5&\", \",\"\")",
        ),
    ],
)
def test_get_references(
    oracle: Oracle, name: str, exclude_sets: Optional[Set[str]], expected: str
) -> None:
    print_refs = xlsx.get_references(oracle.index, name, exclude_sets=exclude_sets)
    assert print_refs == expected


def test_create_all_cards_sheet(oracle: Oracle) -> None:
    book = openpyxl.Workbook()
    sheet = book.create_sheet()
    xlsx.create_all_cards(sheet, oracle.index)
    assert sheet.title == "All Cards"
    rows = [[cell.value for cell in row] for row in sheet.rows]
    assert rows == [
        ["name", "have"],
        ["Air Elemental", '=IF(\'LEA\'!A2>0,"LEA: "&\'LEA\'!A2&", ","")'],
        ["Akroma's Vengeance", '=IF(\'HOP\'!A2>0,"HOP: "&\'HOP\'!A2&", ","")'],
        [
            "Dark Ritual",
            '=IF(\'LEA\'!A3>0,"LEA: "&\'LEA\'!A3&", ","")&'
            'IF(\'ICE\'!A2>0,"ICE: "&\'ICE\'!A2&", ","")&'
            'IF(\'HOP\'!A3>0,"HOP: "&\'HOP\'!A3&", ","")',
        ],
        ["Forest", None],
        ["Rhox", '=IF(\'S00\'!A2>0,"S00: "&\'S00\'!A2&", ","")'],
        ["Snow-Covered Forest", '=IF(\'ICE\'!A6>0,"ICE: "&\'ICE\'!A6&", ","")'],
        [
            "Thallid",
            "=IF('FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5>0,\"FEM: \"&'FEM'!A2+'FEM'!A3+'FEM'!A4+'FEM'!A5&\", \",\"\")",
        ],
    ]


def test_create_set_sheet(oracle: Oracle) -> None:
    card_counts: ScryfallCardCount = {
        UUID("fbdcbd97-90a9-45ea-94f6-2a1c6faaf965"): {CountType.nonfoil: 1},
        UUID("b346b784-7bde-49d0-bfa9-56236cbe19d9"): {CountType.foil: 2},
        UUID("768c4d8f-5700-4f0a-9ff2-58422aeb1dac"): {
            CountType.nonfoil: 3,
            CountType.foil: 4,
        },
    }
    collection = MagicCollection(oracle=oracle, counts=card_counts)
    book = openpyxl.Workbook()
    sheet = book.create_sheet()
    xlsx.create_set_sheet(sheet, collection, "ice")
    assert sheet.title == "ICE"
    rows = [[cell.value for cell in row] for row in sheet.rows]
    assert rows == [
        [
            "have",
            "name",
            "scryfall_id",
            "collector_number",
            "artist",
            "nonfoil",
            "foil",
            "others",
        ],
        [
            "=F2+G2",
            "Dark Ritual",
            "4ebcd681-1871-4914-bcd7-6bd95829f6e0",
            "120",
            "Justin Hampton",
            None,
            None,
            mock.ANY,
        ],
        [
            "=F3+G3",
            "Forest",
            "fbdcbd97-90a9-45ea-94f6-2a1c6faaf965",
            "380",
            "Pat Morrissey",
            1,
            None,
            mock.ANY,
        ],
        [
            "=F4+G4",
            "Forest",
            "b346b784-7bde-49d0-bfa9-56236cbe19d9",
            "381",
            "Pat Morrissey",
            None,
            2,
            mock.ANY,
        ],
        [
            "=F5+G5",
            "Forest",
            "768c4d8f-5700-4f0a-9ff2-58422aeb1dac",
            "382",
            "Pat Morrissey",
            3,
            4,
            mock.ANY,
        ],
        [
            "=F6+G6",
            "Snow-Covered Forest",
            "4c0ad95c-d62c-4138-ada0-fa39a63a449e",
            "383",
            "Pat Morrissey",
            None,
            None,
            mock.ANY,
        ],
    ]


def test_write(oracle: Oracle, tmp_path: Path) -> None:
    xlsx_path = tmp_path / "outfile.xlsx"
    card_counts: ScryfallCardCount = {
        UUID("5d5f3f57-410f-4ee2-b93c-f5051a068828"): {
            CountType.nonfoil: 7,
            CountType.foil: 12,
        }
    }
    collection = MagicCollection(oracle=oracle, counts=card_counts)

    serializer = xlsx.XlsxDialect()
    serializer.write(xlsx_path, collection)

    workbook = openpyxl.load_workbook(filename=xlsx_path)
    assert workbook.sheetnames == [
        "All Sets",
        "All Cards",
        "LEA",
        "FEM",
        "ICE",
        "S00",
        "HOP",
    ]

    s00_rows = [[cell.value for cell in row] for row in workbook["S00"]]
    assert s00_rows == [
        [
            "have",
            "name",
            "scryfall_id",
            "collector_number",
            "artist",
            "nonfoil",
            "foil",
            "others",
        ],
        [
            "=F2+G2",
            "Rhox",
            "5d5f3f57-410f-4ee2-b93c-f5051a068828",
            "43",
            "Mark Zug",
            7,
            12,
            None,
        ],
    ]


@pytest.mark.parametrize(
    "sheets_and_rows, skip_sheets, expected",
    [
        pytest.param(
            [("MySheet", [["A", "B", "C"], ["1", "B", "=5+7"]])],
            None,
            [{"set": "MySheet", "A": "1", "B": "B", "C": "=5+7"}],
        ),
        pytest.param(
            [
                ("MySheet", [["A", "B", "C"], ["1", "B", "=5+7"]]),
                (
                    "OtherSheet",
                    [["D", "E", "F"], ["D1", "E1", "F1"], ["D2", "E2", "F2"]],
                ),
            ],
            None,
            [
                {"set": "MySheet", "A": "1", "B": "B", "C": "=5+7"},
                {"set": "OtherSheet", "D": "D1", "E": "E1", "F": "F1"},
                {"set": "OtherSheet", "D": "D2", "E": "E2", "F": "F2"},
            ],
        ),
        pytest.param(
            [
                ("MySheet", [["A", "B", "C"], ["1", "B", "=5+7"]]),
                (
                    "OtherSheet",
                    [["D", "E", "F"], ["D1", "E1", "F1"], ["D2", "E2", "F2"]],
                ),
            ],
            {"OtherSheet"},
            [{"set": "MySheet", "A": "1", "B": "B", "C": "=5+7"}],
        ),
    ],
)
def test_rows_from_workbook(
    sheets_and_rows: List[Tuple[str, List[List[str]]]],
    skip_sheets: Optional[Set[str]],
    expected: List[Dict[str, str]],
) -> None:
    workbook = openpyxl.Workbook()
    for sheet, rows in sheets_and_rows:
        worksheet = workbook.create_sheet(title=sheet)
        for row in rows:
            worksheet.append(row)
    del workbook["Sheet"]
    assert list(xlsx.rows_for_workbook(workbook, skip_sheets=skip_sheets)) == expected


def test_read_from_file(oracle: Oracle, tmp_path: Path) -> None:
    xlsx_path = tmp_path / "infile.xlsx"
    serializer = xlsx.XlsxDialect()
    workbook = openpyxl.Workbook()
    sheet = workbook["Sheet"]
    sheet.title = "S00"
    sheet.append(["scryfall_id", "nonfoil", "foil"])
    sheet.append(["5d5f3f57-410f-4ee2-b93c-f5051a068828", 3, 7])
    workbook.save(xlsx_path)
    collection = serializer.read(xlsx_path, oracle)
    assert collection.counts == {
        UUID("5d5f3f57-410f-4ee2-b93c-f5051a068828"): {
            CountType.nonfoil: 3,
            CountType.foil: 7,
        }
    }
