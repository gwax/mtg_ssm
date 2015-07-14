"""SQLAlchemy models for managing data."""

import enum
import string

import sqlalchemy as sqla
import sqlalchemy.ext.associationproxy as sqlpxy
import sqlalchemy.ext.declarative as sqld
import sqlalchemy.orm as sqlo
import sqlalchemy.orm.collections as sqlc

from mtgcdb import util


class Base(sqld.declarative_base()):
    __abstract__ = True


class Card(Base):
    """Model for storing card information."""
    __tablename__ = 'cards'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)


class CardPrinting(Base):
    """Model for storing information about card printings."""
    __tablename__ = 'printings'
    __table_args__ = (
        sqla.UniqueConstraint(
            'card_id', 'set_id', 'set_number', 'multiverseid',
            name='uix_card_set_number_mvid'),
        {})

    id = sqla.Column(sqla.Integer, primary_key=True)
    card_id = sqla.Column(sqla.ForeignKey('cards.id'))
    set_id = sqla.Column(sqla.ForeignKey('sets.id'))
    set_number = sqla.Column(sqla.Unicode(15), nullable=True)
    multiverseid = sqla.Column(sqla.Integer, nullable=True)

    artist = sqla.Column(sqla.Unicode(255), nullable=False)

    # Properties
    set_integer = sqlo.column_property(
        sqla.cast(
            sqla.func.trim(set_number, string.ascii_lowercase),
            sqla.Integer))
    set_variant = sqlo.column_property(
        sqla.func.trim(set_number, string.digits))

    # Relationships
    card = sqlo.relationship('Card')
    set = sqlo.relationship('CardSet')
    _counts = sqlo.relationship(
        'CollectionCount',
        collection_class=sqlc.attribute_mapped_collection('key'))
    counts = sqlpxy.association_proxy(
        '_counts', 'count',
        creator=lambda k, v: CollectionCount(type=CountTypes(k), count=v))


class CardSet(Base):
    """Model for storing card set information."""
    __tablename__ = 'sets'

    id = sqla.Column(sqla.Integer, primary_key=True)
    code = sqla.Column(sqla.Unicode(15), unique=True, nullable=False)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)
    block = sqla.Column(sqla.Unicode(255))
    release_date = sqla.Column(sqla.Date)
    type = sqla.Column(sqla.Unicode(255))
    online_only = sqla.Column(sqla.Boolean, default=False)

    # Relationships
    printings = sqlo.relationship('CardPrinting', order_by=(
        CardPrinting.set_integer, CardPrinting.set_variant,
        CardPrinting.multiverseid, CardPrinting.card_id))


class CountTypes(enum.Enum):
    copies = 'copies'
    foils = 'foils'


class CollectionCount(Base):
    """Model for storing information about collected printings."""
    __tablename__ = 'collection_counts'

    print_id = sqla.Column(sqla.ForeignKey('printings.id'), primary_key=True)
    type = sqla.Column(util.SqlEnumType(CountTypes), primary_key=True)
    count = sqla.Column(sqla.Integer, nullable=True)

    @property
    def key(self):
        return self.type.value
