"""SQLAlchemy models for managing data."""

import enum
import string

import sqlalchemy as sqla
import sqlalchemy.ext.associationproxy as sqlpxy
import sqlalchemy.ext.declarative as sqld
import sqlalchemy.orm as sqlo
import sqlalchemy.orm.collections as sqlc

from mtg_ssm.db import util

VARIANT_CHARS = (string.ascii_lowercase + '★')


class Base(sqld.declarative_base()):
    """Abstract base class for declarative models."""
    __abstract__ = True


class Card(Base):
    """Model for storing card information."""
    __tablename__ = 'cards'
    name = sqla.Column(sqla.Unicode(255), primary_key=True)
    strict_basic = sqla.Column(sqla.Boolean, default=False)

    # Relationships
    printings = sqlo.relationship('CardPrinting')


class CardPrinting(Base):
    """Model for storing information about card printings."""
    __tablename__ = 'printings'
    __table_args__ = (
        sqla.UniqueConstraint(
            'card_name', 'set_code', 'set_number', 'multiverseid',
            name='uix_card_set_number_mvid'),
        {})

    id = sqla.Column(sqla.String(40), primary_key=True)
    card_name = sqla.Column(sqla.ForeignKey('cards.name'))
    set_code = sqla.Column(sqla.ForeignKey('sets.code'))

    set_number = sqla.Column(sqla.Unicode(15), nullable=True)
    multiverseid = sqla.Column(sqla.Integer, nullable=True)

    artist = sqla.Column(sqla.Unicode(255), nullable=False)

    # Properties
    set_integer = sqlo.column_property(
        sqla.cast(
            sqla.func.trim(set_number, VARIANT_CHARS),
            sqla.Integer))
    set_variant = sqlo.column_property(
        sqla.func.trim(set_number, string.digits))

    # Relationships
    card = sqlo.relationship('Card', lazy='joined')
    set = sqlo.relationship('CardSet', lazy='subquery')
    collection_counts = sqlo.relationship(
        'CollectionCount', lazy='subquery',
        collection_class=sqlc.attribute_mapped_collection('key'),
        cascade='all, delete-orphan')
    counts = sqlpxy.association_proxy(
        'collection_counts', 'count',
        creator=lambda k, v: CollectionCount(
            type=getattr(CountTypes, k), count=v))


class CardSet(Base):
    """Model for storing card set information."""
    __tablename__ = 'sets'

    code = sqla.Column(sqla.Unicode(15), primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)
    block = sqla.Column(sqla.Unicode(255))
    release_date = sqla.Column(sqla.Date)
    type = sqla.Column(sqla.Unicode(255))
    online_only = sqla.Column(sqla.Boolean, default=False)

    # Relationships
    printings = sqlo.relationship(
        'CardPrinting', order_by=(
            CardPrinting.set_integer, CardPrinting.set_variant,
            CardPrinting.multiverseid, CardPrinting.card_name))

    __mapper_args__ = {
        'order_by': release_date,
    }


class CountTypes(enum.IntEnum):
    """Enum for holding card printing types (normal, foil)."""
    copies = 1
    foils = 2


class CollectionCount(Base):
    """Model for storing information about collected printings."""
    __tablename__ = 'collection_counts'

    print_id = sqla.Column(sqla.ForeignKey('printings.id'), primary_key=True)
    type = sqla.Column(util.SqlEnumType(CountTypes), primary_key=True)
    count = sqla.Column(sqla.Integer, nullable=False)

    @property
    def key(self):
        """Model key for use in associationproxy relationships."""
        return self.type.name
