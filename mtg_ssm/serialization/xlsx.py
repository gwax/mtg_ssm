"""XLSX serializer."""

import collections
import string

import openpyxl

from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface


ALL_SETS_SHEET_HEADER = [
    'code',
    'name',
    'release',
    'block',
    'type',
    'cards',
    'unique',
    'playsets',
    'count',
]

ALL_SETS_SHEET_TOTALS = [
    'Total',
    None,
    None,
    None,
    None,
    '=SUM(F3:F65535)',
    '=SUM(G3:G65535)',
    '=SUM(H3:H65535)',
    '=SUM(I3:I65535)',
]


def create_all_sets(sheet, collection):
    """Create all sets sheet from collection."""
    sheet.title = 'All Sets'
    sheet.append(ALL_SETS_SHEET_HEADER)
    sheet.append(ALL_SETS_SHEET_TOTALS)
    for card_set in collection.card_sets:
        row = [
            card_set.code,
            card_set.name,
            card_set.release_date,
            card_set.block,
            card_set.type_,
            len(card_set.printings),
            '=COUNTIF(\'{}\'!A:A,">0")'.format(card_set.code),
            '=COUNTIF(\'{}\'!A:A,">=4")'.format(card_set.code),
            "=SUM('{}'!A:A)".format(card_set.code),
        ]
        sheet.append(row)


def style_all_sets(sheet):
    """Apply styles to the all sets sheet."""
    sheet.freeze_panes = sheet['C3']
    col_width_hidden = [
        ('A', 6, False),
        ('B', 24, False),
        ('C', 12, True),
        ('D', 16, True),
        ('E', 12, True),
        ('F', 6, False),
        ('G', 7, False),
        ('H', 8, False),
        ('I', 7, False),
    ]
    for col, width, hidden in col_width_hidden:
        cdim = sheet.column_dimensions[col]
        cdim.width = width
        cdim.hidden = hidden


SET_SHEET_HEADER = [
    'have',
    'name',
    'id',
    'multiverseid',
    'number',
    'artist',
] + [ct.name for ct in models.CountTypes] + [
    'others',
]
COUNT_COLS = [
    string.ascii_uppercase[SET_SHEET_HEADER.index(ct.name)]
    for ct in models.CountTypes]
HAVE_TMPL = '=' + '+'.join(c + '{0}' for c in COUNT_COLS)
ROW_OFFSET = 2


def create_haverefs(printings):
    """Create a reference to the have cells for printings in a single set."""
    card_set = printings[0].set
    rownums = [card_set.printings.index(p) + ROW_OFFSET for p in printings]
    haverefs = [
        "'{setcode}'!A{rownum}".format(setcode=card_set.code, rownum=r)
        for r in rownums]
    return '+'.join(haverefs)


def get_other_print_references(printing):
    """Get an xlsx formula to list counts of a card from other sets."""
    if printing.card.strict_basic:
        return None  # Basics are so prolific that they overwhelm Excel

    set_to_others = collections.defaultdict(list)
    for other in printing.card.printings:
        if other.set_code != printing.set_code:
            set_to_others[other.set].append(other)

    set_to_haveref = {k: create_haverefs(v) for k, v in set_to_others.items()}
    if not set_to_haveref:
        return None

    other_references = []
    for card_set in sorted(set_to_haveref, key=lambda cset: cset.release_date):
        other_reference = 'IF({count}>0,"{setcode}: "&{count}&", ","")'.format(
            setcode=card_set.code, count=set_to_haveref[card_set])
        other_references.append(other_reference)
    return '=' + '&'.join(other_references)


def create_set_sheet(sheet, card_set):
    """Populate sheet with card information from a given set."""
    sheet.title = card_set.code
    sheet.append(SET_SHEET_HEADER)
    for printing in card_set.printings:
        rownum = card_set.printings.index(printing) + ROW_OFFSET
        row = [
            HAVE_TMPL.format(rownum),
            printing.card.name,
            printing.id_,
            printing.multiverseid,
            printing.set_number,
            printing.artist,
        ]
        for counttype in models.CountTypes:
            row.append(printing.counts.get(counttype))
        row.append(get_other_print_references(printing))
        sheet.append(row)


def style_set_sheet(sheet):
    """Apply styles to a set sheet."""
    sheet.freeze_panes = sheet['C2']
    col_width_hidden = [
        ('A', 5, False),
        ('B', 18, False),
        ('C', 5, True),
        ('D', 12, True),
        ('E', 8, True),
        ('F', 20, True),
        ('G', 6, False),
        ('H', 6, False),
        ('I', 10, False),
    ]
    for col, width, hidden in col_width_hidden:
        cdim = sheet.column_dimensions[col]
        cdim.width = width
        cdim.hidden = hidden


def counts_from_sheet(sheet):
    """Given an xlsx set sheet, read card counts."""
    rows = iter(sheet.rows)
    header = [cell.value for cell in next(rows)]
    for row in rows:
        row_values = [cell.value for cell in row]
        yield dict(zip(header, row_values))


class MtgXlsxSerializer(interface.MtgSsmSerializer):
    """MtgSsmSerializer for reading and writing xlsx files."""

    format = 'xlsx'
    extension = 'xlsx'

    def write_to_file(self, filename: str) -> None:
        """Write the collection to an xlsx file."""
        workbook = openpyxl.Workbook()
        all_sets_sheet = workbook.create_sheet()
        create_all_sets(all_sets_sheet, self.collection)
        style_all_sets(all_sets_sheet)
        for card_set in self.collection.card_sets:
            set_sheet = workbook.create_sheet()
            create_set_sheet(set_sheet, card_set)
            style_set_sheet(set_sheet)
        workbook.remove_sheet(workbook['Sheet'])
        workbook.save(filename)

    def read_from_file(self, filename: str) -> None:
        """Read collection counts from xlsx file."""
        workbook = openpyxl.load_workbook(filename=filename, read_only=True)
        for sheet in workbook.worksheets:
            if sheet.title not in self.collection.code_to_card_set:
                if sheet.title in ['Sets', 'All Sets']:
                    continue
                raise interface.DeserializationError(
                    'No known set with code {}'.format(sheet.title))
            for counts in counts_from_sheet(sheet):
                self.load_counts(counts)
