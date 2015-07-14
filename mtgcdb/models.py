"""SQLAlchemy models for managing data."""

import string

import sqlalchemy as sqla
import sqlalchemy.ext.declarative as sqld
import sqlalchemy.orm as sqlo


class Base(sqld.declarative_base()):
    __abstract__ = True


class Card(Base):
    """Model for storing card information."""
    __tablename__ = 'cards'

    name = sqla.Column(sqla.Unicode(255), nullable=False, primary_key=True)
    set_code = sqla.Column(
        sqla.Unicode(15), sqla.ForeignKey('sets.code'), nullable=False,
        primary_key=True)
    set_number = sqla.Column(sqla.Unicode(15), nullable=True, primary_key=True)
    multiverseid = sqla.Column(sqla.Integer, nullable=True, primary_key=True)

    artist = sqla.Column(sqla.Unicode(255), nullable=False)

    # Properties
    set_integer = sqlo.column_property(sqla.cast(
        sqla.func.trim(set_number, string.ascii_lowercase),
        sqla.Integer))
    set_variant = sqlo.column_property(
        sqla.func.trim(set_number, string.digits))

    # Relationships
    set = sqlo.relationship('CardSet')


class CardSet(Base):
    """Model for storing card set information."""
    __tablename__ = 'sets'

    code = sqla.Column(sqla.Unicode(15), nullable=False, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)
    block = sqla.Column(sqla.Unicode(255))
    release_date = sqla.Column(sqla.Date)
    type = sqla.Column(sqla.Unicode(255))
    online_only = sqla.Column(sqla.Boolean, default=False)

    # Relationships
    cards = sqlo.relationship('Card', order_by=(
        Card.set_integer, Card.set_variant, Card.multiverseid, Card.name))
