"""XLSX serializer."""

import collections
import datetime as dt
import string
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import openpyxl
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from mtg_ssm.containers import counts
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.indexes import Oracle, ScryfallDataIndex
from mtg_ssm.mtg import util
from mtg_ssm.scryfall.models import ScryCard, ScrySet
from mtg_ssm.serialization import interface

ALL_SETS_SHEET_HEADER: Sequence[str] = [
    "code",
    "name",
    "release",
    "block",
    "type",
    "cards",
    "unique",
    "playsets",
    "count",
]

ALL_SETS_SHEET_TOTALS: Sequence[Optional[str]] = ["Total", None, None, None, None] + [
    f"=SUM({c}3:{c}65535)" for c in "FGHI"
]


def _card_set_sort_key(cset: ScrySet) -> Tuple[dt.date, str]:
    released_at = cset.released_at or dt.date.min
    return released_at, cset.code


def create_all_sets(sheet: Worksheet, index: ScryfallDataIndex) -> None:
    """Create all sets sheet from card_db."""
    sheet.title = "All Sets"
    sheet.append(ALL_SETS_SHEET_HEADER)
    sheet.append(ALL_SETS_SHEET_TOTALS)
    for card_set in sorted(index.setcode_to_set.values(), key=_card_set_sort_key):
        setcode = card_set.code.upper()
        row = [
            setcode,
            card_set.name,
            card_set.released_at,
            card_set.block,
            card_set.set_type.value,
            len(index.setcode_to_cards[card_set.code]),
            f"=COUNTIF('{setcode}'!A:A,\">0\")",
            f"=COUNTIF('{setcode}'!A:A,\">=4\")",
            f"=SUM('{setcode}'!A:A)",
        ]
        sheet.append(row)


def style_all_sets(sheet: Worksheet) -> None:
    """Apply styles to the all sets sheet."""
    sheet.freeze_panes = sheet["C3"]
    col_width_hidden = [
        ("A", 8, False),
        ("B", 30, False),
        ("C", 12, True),
        ("D", 22, True),
        ("E", 15, True),
        ("F", 6, False),
        ("G", 7, False),
        ("H", 8, False),
        ("I", 7, False),
    ]
    for col, width, hidden in col_width_hidden:
        cdim = sheet.column_dimensions[col]
        cdim.width = width
        cdim.hidden = hidden


def create_haverefs(index: ScryfallDataIndex, cards: Sequence[ScryCard]) -> str:
    """Create a reference to the have cells for printings in a single set."""
    setcodes_and_rownums = sorted(
        (c.set, index.id_to_setindex[c.id] + ROW_OFFSET) for c in cards
    )
    haverefs = [
        f"'{setcode.upper()}'!A{rownum}" for setcode, rownum in setcodes_and_rownums
    ]
    return "+".join(haverefs)


def get_references(
    index: ScryfallDataIndex, card_name: str, exclude_sets: Optional[Set[str]] = None
) -> Optional[str]:
    """Get an equation for the references to a card."""
    if util.is_strict_basic(card_name):
        return None  # Basics are so prolific that they overwhelm Excel

    if exclude_sets is None:
        exclude_sets = set()

    set_to_cards: Dict[str, List[ScryCard]] = collections.defaultdict(list)
    for other_card in index.name_to_cards[card_name]:
        if other_card.set not in exclude_sets:
            set_to_cards[other_card.set].append(other_card)

    set_to_haveref = {k: create_haverefs(index, v) for k, v in set_to_cards.items()}
    if not set_to_haveref:
        return None

    references = []
    for card_set in sorted(
        set_to_haveref,
        key=lambda setcode: _card_set_sort_key(index.setcode_to_set[setcode]),
    ):
        reference = 'IF({count}>0,"{setcode}: "&{count}&", ","")'.format(
            setcode=card_set.upper(), count=set_to_haveref[card_set]
        )
        references.append(reference)
    return "=" + "&".join(references)


ALL_CARDS_SHEET_HEADER = ["name", "have"]  # TODO: add list of sets


def create_all_cards(sheet: Worksheet, index: ScryfallDataIndex) -> None:
    """Create all cards sheet from card_db."""
    sheet.title = "All Cards"
    sheet.append(ALL_CARDS_SHEET_HEADER)
    for name in sorted(index.name_to_cards):
        row = [name, get_references(index, name)]
        sheet.append(row)


def style_all_cards(sheet: Worksheet) -> None:
    """Apply styles to the all cards sheet."""
    sheet.freeze_panes = sheet["B2"]
    col_width_hidden = [("A", 24, False), ("B", 32, False)]
    for col, width, hidden in col_width_hidden:
        cdim = sheet.column_dimensions[col]
        cdim.width = width
        cdim.hidden = hidden


SET_SHEET_HEADER = (
    ["have", "name", "scryfall_id", "collector_number", "artist"]
    + [ct.value for ct in counts.CountType]
    + ["others"]
)
COUNT_COLS = [
    string.ascii_uppercase[SET_SHEET_HEADER.index(ct.value)] for ct in counts.CountType
]
HAVE_TMPL = "=" + "+".join(c + "{rownum}" for c in COUNT_COLS)
ROW_OFFSET = 2


def create_set_sheet(
    sheet: Worksheet, collection: MagicCollection, setcode: str
) -> None:
    """Populate sheet with card information from a given set."""
    index = collection.oracle.index

    sheet.append(SET_SHEET_HEADER)
    sheet.title = setcode.upper()

    for card in index.setcode_to_cards[setcode]:
        rownum = ROW_OFFSET + index.id_to_setindex[card.id]
        row: List[Optional[Any]] = [
            HAVE_TMPL.format(rownum=rownum),
            card.name,
            str(card.id),
            card.collector_number,
            card.artist,
        ]
        card_counts = collection.counts.get(card.id, {})
        for count_type in counts.CountType:
            row.append(card_counts.get(count_type))
        row.append(get_references(index, card.name, exclude_sets={setcode}))
        sheet.append(row)


def style_set_sheet(sheet: Worksheet) -> None:
    """Apply styles to a set sheet."""
    sheet.freeze_panes = sheet["C2"]
    col_width_hidden = [
        ("A", 5, False),
        ("B", 24, False),
        ("C", 10, True),
        ("D", 8, True),
        ("E", 20, True),
        ("F", 8, False),
        ("G", 6, False),
        ("H", 10, False),
    ]
    for col, width, hidden in col_width_hidden:
        cdim = sheet.column_dimensions[col]
        cdim.width = width
        cdim.hidden = hidden


def rows_from_sheet(sheet: Worksheet) -> Iterable[Dict[str, str]]:
    """Read rows from an xlsx worksheet as dicts."""
    header_row, *rows = iter(sheet.rows)
    header = [cell.value for cell in header_row]
    for row in rows:
        values = [cell.value for cell in row]
        if any(v is not None for v in values):
            yield dict(zip(header, values), set=sheet.title)


def rows_for_workbook(
    book: Workbook, *, skip_sheets: Optional[Set[str]]
) -> Iterable[Dict[str, str]]:
    """Read rows from an xlsx workbook as dicts."""
    if skip_sheets is None:
        skip_sheets = set()
    for sheet in book.worksheets:
        if sheet.title in skip_sheets:
            continue
        yield from rows_from_sheet(sheet)


class XlsxDialect(interface.SerializationDialect):
    """excel xlsx collection"""

    extension: ClassVar[str] = "xlsx"
    dialect: ClassVar[str] = "xlsx"

    def write(self, path: Path, collection: MagicCollection) -> None:
        """Write collection to an xlsx file."""
        workbook = openpyxl.Workbook()

        all_sets_sheet = workbook.create_sheet()
        create_all_sets(all_sets_sheet, collection.oracle.index)
        style_all_sets(all_sets_sheet)

        all_cards_sheet = workbook.create_sheet()
        create_all_cards(all_cards_sheet, collection.oracle.index)
        style_all_cards(all_cards_sheet)

        setcodes = [
            s.code
            for s in sorted(
                collection.oracle.index.setcode_to_set.values(),
                key=_card_set_sort_key,
            )
        ]

        for setcode in setcodes:
            set_sheet = workbook.create_sheet()
            create_set_sheet(set_sheet, collection, setcode)
            style_set_sheet(set_sheet)
        del workbook["Sheet"]
        workbook.save(str(path))

    def read(self, path: Path, oracle: Oracle) -> MagicCollection:
        """Read collection from an xlsx file."""
        workbook = openpyxl.load_workbook(filename=str(path), read_only=True)
        reader = rows_for_workbook(workbook, skip_sheets={"All Sets", "All Cards"})
        card_counts = counts.aggregate_card_counts(reader, oracle)
        return MagicCollection(oracle=oracle, counts=card_counts)
