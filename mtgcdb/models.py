"""SQLAlchemy models for managing data."""

import sqlalchemy as sqla
import sqlalchemy.ext.declarative as sqld
import sqlalchemy.orm as sqlo


class Base(sqld.declarative_base()):
    __abstract__ = True


class CardType(Base):
    """Model for card types."""
    __tablename__ = 'card_types'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)


CARD_TYPE_ASSOCIATION = sqla.Table(
    'cards_card_types', Base.metadata,
    sqla.Column('card_id', sqla.Integer, sqla.ForeignKey('cards.id'),
                primary_key=True),
    sqla.Column('card_type_id', sqla.Integer, sqla.ForeignKey('card_types.id'),
                primary_key=True))


class CardSupertype(Base):
    """Model for card super types."""
    __tablename__ = 'card_supertypes'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)


CARD_SUPERTYPE_ASSOCIATION = sqla.Table(
    'card_card_supertypes', Base.metadata,
    sqla.Column('card_id', sqla.Integer, sqla.ForeignKey('cards.id'),
                primary_key=True),
    sqla.Column('card_supertype_id', sqla.Integer,
                sqla.ForeignKey('card_supertypes.id'), primary_key=True))


class Card(Base):
    """Model for storing a card, abstract of printings."""
    __tablename__ = 'cards'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)

    # Relationships
    types = sqlo.relationship(
        'CardType', secondary='cards_card_types', collection_class=set)
    supertypes = sqlo.relationship(
        'CardSupertype', secondary='card_card_supertypes', collection_class=set)
    printings = sqlo.relationship('CardPrinting')


class Artist(Base):
    """Model for card printing artists."""
    __tablename__ = 'artists'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)


class CardPrinting(Base):
    """Model for card printing, relating a card to a set."""
    __tablename__ = 'card_printings'

    id = sqla.Column(sqla.Integer, primary_key=True)
    _card_id = sqla.Column(
        'card_id', sqla.Integer, sqla.ForeignKey('cards.id'), nullable=False)
    _set_id = sqla.Column(
        'set_id', sqla.Integer, sqla.ForeignKey('sets.id'), nullable=False)
    _artist_id = sqla.Column(
        'artist_id', sqla.Integer, sqla.ForeignKey('artists.id'))

    set_number = sqla.Column(sqla.Unicode(15))
    multiverseid = sqla.Column(sqla.Integer)

    # Relationships
    card = sqlo.relationship('Card')
    set = sqlo.relationship('CardSet')
    artist = sqlo.relationship('Artist')


class CardBlock(Base):
    """Model for a block of sets."""
    __tablename__ = 'blocks'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)


class CardSet(Base):
    """Model for storing a set of cards."""
    __tablename__ = 'sets'

    id = sqla.Column(sqla.Integer, primary_key=True)
    _block_id = sqla.Column('block_id', sqla.Integer,
                            sqla.ForeignKey('blocks.id'))

    code = sqla.Column(sqla.Unicode(15), unique=True, nullable=False)
    name = sqla.Column(sqla.Unicode(255), unique=True, nullable=False)
    release_date = sqla.Column(sqla.Date)
    type = sqla.Column(sqla.Unicode(255))
    online_only = sqla.Column(sqla.Boolean, default=False)

    # Relationships
    block = sqlo.relationship('CardBlock')
    cards = sqlo.relationship('CardPrinting')
