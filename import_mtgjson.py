#!/usr/bin/env python3
"""Import data from mtgjson."""

import collections
import json
import os

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

from mtgcdb import models
from mtgcdb import mtgjson

DB_FILE = 'mtgcdb.sqlite'
MTGJSON_FILE = os.path.join('data', 'AllSets.json')


def main():
    """Import data from AllSets.json to mtgcdb.sqlite"""
    with open(MTGJSON_FILE, 'r') as mtgjsonfile:
        mtgdata = json.load(
            mtgjsonfile, object_pairs_hook=collections.OrderedDict)
    engine = sqla.create_engine('sqlite:///{}'.format(DB_FILE))
    session_factory = sqlo.sessionmaker(engine)
    session = session_factory()
    try:
        connection = session.connection()
        models.Base.metadata.create_all(connection)
        mtgjson.update_models(session, mtgdata)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
