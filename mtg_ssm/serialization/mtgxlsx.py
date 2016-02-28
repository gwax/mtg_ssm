"""Code for handling data in xlsx files."""

import collections
import string

import openpyxl

from mtg_ssm.mtg import models
from mtg_ssm.serialization import mtgdict


def dump_workbook(collection):
    """Return xlsx workbook from a Collection."""
    workbook = openpyxl.Workbook()

    card_sets = sorted(
        collection.code_to_card_set.values(),
        key=lambda cset: cset.release_date)

    sets_sheet = workbook['Sheet']
    create_sets_sheet(sets_sheet, card_sets)
    for card_set in card_sets:
        cards_sheet = workbook.create_sheet()
        create_cards_sheet(cards_sheet, card_set)
    return workbook


SETS_SHEET_HEADER = [
    'code', 'name', 'release', 'block', 'type', 'cards', 'unique', 'playsets',
    'count']


def create_sets_sheet(sheet, card_sets):
    """Populate sheet with information about all card sets."""
    sheet.title = 'Sets'
    sheet.append(SETS_SHEET_HEADER)
    sheet.append([
        'Total',
        None,
        None,
        None,
        None,
        '=SUM(F3:F65535)',
        '=SUM(G3:G65535)',
        '=SUM(H3:H65535)',
        '=SUM(I3:I63353)',
    ])
    for card_set in card_sets:
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

    # Styling
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


def split_into_consecutives(numlist):
    """Split a list of numbers into lists of consecutive groups."""
    if not numlist:
        return []
    numlist.sort()
    retlist = [[]]
    current_group = retlist[0]
    previous = numlist[0] - 1
    for val in numlist:
        if previous + 1 == val:
            current_group.append(val)
        else:
            current_group = [val]
            retlist.append(current_group)
        previous = val
    return retlist


def create_haveref_sum(setcode, rownums):
    """Given a setcode and list of rownumbers, create a sum of have cells."""
    haverefs = []
    for sequence in split_into_consecutives(rownums):
        if len(sequence) == 1:
            haverefs.append("'{0}'!A{1}".format(setcode, sequence[0]))
        else:
            haverefs.append(
                "SUM('{0}'!A{1}:A{2})".format(
                    setcode, sequence[0], sequence[-1]))
    return '+'.join(haverefs)


def get_other_print_references(printing):
    """Get an xlsx formula to list counts of a card from other sets."""
    if printing.card.strict_basic:
        return None  # Basics are so prolific, they tend to bog things down
    other_prints = (
        p for p in printing.card.printings
        if p.set_code != printing.set_code)
    setcode_and_release = set()
    setcode_to_rownums = collections.defaultdict(list)
    for other in other_prints:
        other_set = other.set
        setcode_and_release.add((other_set.code, other_set.release_date))
        setcode_to_rownums[other_set.code].append(
            other_set.printings.index(other) + 2)
    if not setcode_to_rownums:
        return None
    setcode_and_release = sorted(setcode_and_release, key=lambda item: item[1])
    set_to_havecellref = collections.OrderedDict()
    for setcode, _ in setcode_and_release:
        rownums = setcode_to_rownums[setcode]
        set_to_havecellref[setcode] = create_haveref_sum(setcode, rownums)
    other_print_references = '=' + '&'.join(
        'IF({1}>0,"{0}: "&{1}&", ","")'.format(k, v)
        for k, v in set_to_havecellref.items())
    return other_print_references


COUNT_KEYS = [ct.name for ct in models.CountTypes]
CARDS_SHEET_HEADER = (
    ['have', 'name', 'id', 'multiverseid', 'number', 'artist'] +
    COUNT_KEYS + ['others'])
COUNT_COLS = [
    string.ascii_uppercase[CARDS_SHEET_HEADER.index(k)] for k in COUNT_KEYS]
HAVE_TMPL = '=' + '+'.join(c + '{0}' for c in COUNT_COLS)
ROW_OFFSET = 2


def create_cards_sheet(sheet, card_set):
    """Populate sheet with card information from a given set."""
    sheet.title = card_set.code
    sheet.append(CARDS_SHEET_HEADER)
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

    # Styling
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


def read_workbook_counts(collection, workbook):
    """Read mtgxlsx workbook and load counts into a Collection."""
    set_codes = collection.code_to_card_set.keys()
    card_dicts = workbook_row_reader(workbook, set_codes)
    mtgdict.load_counts(collection, card_dicts)


def workbook_row_reader(workbook, known_sets):
    """Given a workbook, yield card_dicts suitable for mtgdict."""
    for sheet in workbook.worksheets:
        set_code = sheet.title
        if set_code not in known_sets:
            if set_code != 'Sets':
                print('No known set with code "{}", skipping.'.format(set_code))
            continue
        for row_dict in worksheet_row_reader(sheet):
            row_dict['set'] = set_code
            yield row_dict


def worksheet_row_reader(worksheet):
    """Given a worksheet, yield card_dicts."""
    row_iter = iter(worksheet.rows)
    header = [cell.value for cell in next(row_iter)]
    for row in row_iter:
        row_values = [cell.value for cell in row]
        row_dict = dict(zip(header, row_values))
        yield row_dict
