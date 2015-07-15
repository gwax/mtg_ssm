#!/usr/bin/env python3
"""Import data from xlsx."""

import openpyxl

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

from mtgcdb import mtgxlsx

DB_FILE = 'mtgcdb.sqlite'
XLSX_FILE = 'mtgcdb.xlsx'


def main():
    """Import data from mtgcdb.xlsx to mtgcdb.sqlite"""
    engine = sqla.create_engine('sqlite:///{}'.format(DB_FILE))
    session_factory = sqlo.sessionmaker(engine)
    session = session_factory()
    try:
        workbook = openpyxl.load_workbook(filename=XLSX_FILE, read_only=True)
        mtgxlsx.read_workbook_counts(session, workbook)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
