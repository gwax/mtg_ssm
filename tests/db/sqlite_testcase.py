"""Testcase for tests that require a sqlalchemy sqlite engine."""

import unittest

import sqlalchemy
import sqlalchemy.event
import sqlalchemy.orm


def set_sqlite_pragma(dbapi_connection, _connection_record):
    """Listener handler to enable foreign key pragmas on connect."""
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


class SqliteTestCase(unittest.TestCase):
    """TestCase that creates an sqlite database for testing."""

    def setUp(self):
        super().setUp()
        self.engine = sqlalchemy.create_engine('sqlite://')
        sqlalchemy.event.listen(self.engine, 'connect', set_sqlite_pragma)

        self.sessionmaker = sqlalchemy.orm.sessionmaker(self.engine)
        self.session = self.__session = self.sessionmaker()

    def tearDown(self):
        self.__session.close()
        self.engine.dispose()
        super().tearDown()
