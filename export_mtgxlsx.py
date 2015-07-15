#!/usr/bin/env python3
"""Export data to xlsx."""

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

from mtgcdb import mtgxlsx

DB_FILE = 'mtgcdb.sqlite'
XLSX_FILE = 'mtgcdb.xlsx'


def main():
    """Export data from mtgcdb.sqlite to mtgcdb.xlsx"""
    engine = sqla.create_engine('sqlite:///{}'.format(DB_FILE))
    session_factory = sqlo.sessionmaker(engine)
    session = session_factory()
    try:
        workbook = mtgxlsx.dump_workbook(session)
        workbook.save(XLSX_FILE)
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
