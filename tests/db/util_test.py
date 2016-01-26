"""Tests for mtg_ssm.util"""

import enum

import sqlalchemy as sqla
import sqlalchemy.ext.declarative as sqld

from mtg_ssm.db import util

from tests.db import sqlite_testcase


class MyEnum(enum.IntEnum):
    """Simple enum to test SqlEnumType."""
    one = 1
    two = 2


class Model(sqld.declarative_base()):
    """Simple declarative model to test enum handling."""
    __tablename__ = 'test'

    id = sqla.Column(sqla.Integer, primary_key=True)
    enum_col = sqla.Column(util.SqlEnumType(MyEnum))


class SqlEnumTest(sqlite_testcase.SqliteTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        Model.metadata.create_all(connection)
        connection.close()

    def test_store_retrieve(self):
        # Store
        self.session.add(Model(id=1, enum_col=MyEnum.one))
        self.session.add(Model(id=2, enum_col=MyEnum.two))
        self.session.commit()

        # Retrieve
        objs = self.session.query(Model).all()
        obj_dicts = [{'id': o.id, 'enum_col': o.enum_col} for o in objs]
        expected = [
            {'id': 1, 'enum_col': MyEnum.one},
            {'id': 2, 'enum_col': MyEnum.two},
        ]
        self.assertEqual(expected, obj_dicts)

    def test_db_strings(self):
        # Setup
        self.session.add(Model(id=1, enum_col=MyEnum.one))
        self.session.add(Model(id=2, enum_col=MyEnum.two))
        self.session.commit()

        # Verify
        connection = self.engine.connect()
        rows = connection.execute('SELECT * FROM test')
        id_to_enum_col = {r['id']: r['enum_col'] for r in rows}
        connection.close()
        expected = {
            1: 'one',
            2: 'two',
        }
        self.assertEqual(expected, id_to_enum_col)
