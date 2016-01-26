"""General helper methods and classes."""

import re

import sqlalchemy.types as sqlt


class SqlEnumType(sqlt.SchemaType, sqlt.TypeDecorator):
    """Type class for storing a python3 enum in SQL.

    Derived from: http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    """

    def __init__(self, enum_cls):
        """Given an enum.IntEnum create a sqlalchemy type to store it."""
        super().__init__()
        values = [member.name for member in enum_cls.__members__.values()]
        name = 'ck{}'.format(re.sub(
            '([A-Z])', lambda match: '_' + match.group(1).lower(),
            enum_cls.__name__))
        self.enum = enum_cls
        self.impl = sqlt.Enum(*values, name=name)

    def _set_table(self, column, table):
        self.impl._set_table(column, table)  # pylint: disable=protected-access

    def copy(self):
        return self.__class__(self.enum)

    def process_literal_param(self, value, _dialect):
        return value

    def process_bind_param(self, value, _dialect):
        return None if value is None else value.name

    def process_result_value(self, value, _dialect):
        return None if value is None else getattr(self.enum, value)
