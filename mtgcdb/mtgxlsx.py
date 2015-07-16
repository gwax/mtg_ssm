"""Code for handling data in xlsx files."""

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
    header = ['code', 'name', 'release', 'block', 'type', 'cards']
    sheet.append(header)
    for card_set in card_sets:
        row = [
            card_set.code,
            card_set.name,
            card_set.release_date,
            card_set.block,
            card_set.type,
            len(card_set.printings),
        ]
        sheet.append(row)

def create_cards_sheet(sheet, card_set):
    """Populate sheet with card information from a given set."""
    sheet.title = card_set.code
    header = ['name', 'multiverseid', 'number', 'artist']
    header.extend(models.CountTypes.__members__.keys())
    sheet.append(header)
    for printing in card_set.printings:
        row = [
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
