"""Code for handling data in xlsx files."""

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
    workbook = openpyxl.Workbook(write_only=True)
    sets_sheet = workbook.create_sheet()
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

def create_cards_sheet(sheet, card_set):
    """Populate sheet with card information from a given set."""
    sheet.title = card_set.code
    base_header = ['have', 'name', 'multiverseid', 'number', 'artist']
    header = base_header + list(models.CountTypes.__members__.keys())
    count_cols = (
        string.ascii_uppercase[i] for i in
        range(len(base_header), len(header)))
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
        sheet.append(row)


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
