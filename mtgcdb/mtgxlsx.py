"""Code for handling data in xlsx files."""

import collections
import string

import openpyxl
import sqlalchemy.orm as sqlo

from mtgcdb import models
from mtgcdb import mtgdict


def dump_workbook(session):
    """Return xlsx workbook from the database."""
    card_sets = session.query(models.CardSet) \
        .options(sqlo.subqueryload('printings').joinedload('card')) \
        .order_by(models.CardSet.release_date) \
        .all()
    workbook = openpyxl.Workbook()
    sets_sheet = workbook['Sheet']
    create_sets_sheet(sets_sheet, card_sets)
    for card_set in card_sets:
        cards_sheet = workbook.create_sheet()
        create_cards_sheet(cards_sheet, card_set)
    return workbook


def create_sets_sheet(sheet, card_sets):
    """Populate sheet with information about all card sets."""
    sheet.title = 'Sets'
    header = [
        'code', 'name', 'release', 'block', 'type', 'cards', 'unique',
        'playsets', 'count']
    sheet.append(header)
    for card_set in card_sets:
        row = [
            card_set.code,
            card_set.name,
            card_set.release_date,
            card_set.block,
            card_set.type,
            len(card_set.printings),
            '=COUNTIF(\'{}\'!A:A,">0")'.format(card_set.code),
            '=COUNTIF(\'{}\'!A:A,">=4")'.format(card_set.code),
            "=SUM('{}'!A:A)".format(card_set.code)
        ]
        sheet.append(row)
    sheet.freeze_panes = sheet['C2']
    widths = [10, 30, 12, 16, 12, 7, 7, 7, 7]
    for width, cdim in zip(widths, sheet.column_dimensions.values()):
        cdim.width = width


def get_other_print_references(printing):
    """Get an xlsx formula to list counts of a card from other sets."""
    setcode_to_rownums = collections.defaultdict(list)
    setcode_and_release = set()
    for other in printing.card.printings:
        if other.set_id == printing.set_id:
            continue
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
        haverefs = ["'{0}'!A{1}".format(setcode, rownum) for rownum in rownums]
        havecellref = '+'.join(haverefs)
        set_to_havecellref[setcode] = havecellref
    other_print_references = '=' + '&'.join(
        'IF({1}>0,"{0}: "&{1}&", ","")'.format(k, v)
        for k, v in set_to_havecellref.items())
    return other_print_references


def create_cards_sheet(sheet, card_set):
    """Populate sheet with card information from a given set."""
    sheet.title = card_set.code
    header = ['have', 'name', 'multiverseid', 'number', 'artist']
    count_keys = list(models.CountTypes.__members__.keys())
    header.extend(count_keys)
    header.append('others')
    count_cols = [
        string.ascii_uppercase[header.index(key)] for key in count_keys]
    have_tmpl = '=' + '+'.join(c + '{0}' for c in count_cols)
    sheet.append(header)
    for printing in card_set.printings:
        rownum = card_set.printings.index(printing) + 2
        row = [
            have_tmpl.format(rownum),
            printing.card.name,
            printing.multiverseid,
            printing.set_number,
            printing.artist,
        ]
        for key in models.CountTypes.__members__.keys():
            row.append(printing.counts.get(key))
        row.append(get_other_print_references(printing))
        sheet.append(row)
    sheet.freeze_panes = sheet['C2']
    widths = [6, 25, 12, 8, 20, 6, 6, 10]
    for width, cdim in zip(widths, sheet.column_dimensions.values()):
        cdim.width = width


def read_workbook_counts(session, workbook):
    """Read mtgxlsx workbook and load counts into the database."""
    for worksheet in workbook.worksheets:
        read_worksheet_counts(session, worksheet)

def read_worksheet_counts(session, worksheet):
    """Read mtgxlsx worksheet and load counts into database."""
    card_set = session.query(models.CardSet) \
        .filter_by(code=worksheet.title) \
        .first()
    if card_set is None:
        return
    row_iter = iter(worksheet.rows)

    header = [c.value for c in next(row_iter)]
    rows = ([c.value for c in row] for row in row_iter)
    row_dicts = (dict(zip(header, row)) for row in rows)
    for row_dict in row_dicts:
        row_dict['set'] = card_set.code
        mtgdict.load_counts(session, row_dict)
