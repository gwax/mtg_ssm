"""SQLAlchemy models for managing data."""

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
    cards = sqlo.relationship('Card')  # TODO(george): order_by
