#!/usr/bin/env python3
"""Export data to csv."""

import csv

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

from mtgcdb import mtgcsv

DB_FILE = 'mtgcdb.sqlite'
CSV_FILE = 'mtgcdb.csv'


def main():
    """Export data from mtgcdb.sqlite to mtgcdb.csv"""
    engine = sqla.create_engine('sqlite:///{}'.format(DB_FILE))
    session_factory = sqlo.sessionmaker(engine)
    session = session_factory()
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            mtgcsv.read_row_counts(session, reader)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
