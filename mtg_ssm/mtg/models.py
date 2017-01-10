"""Models for managing data."""

import datetime as dt
import string
import weakref

VARIANT_CHARS = (string.ascii_letters + '★')
STRICT_BASICS = {'Plains', 'Island', 'Swamp', 'Mountain', 'Forest'}


class Card:
    """Model for storing card information."""
    __slots__ = ('cdb', 'name', 'layout', 'names')

    def __init__(self, card_db, card_data):
        self.cdb = weakref.proxy(card_db)
        self.name = card_data['name']
        self.layout = card_data['layout']
        self.names = card_data.get('names', [self.name])

    @property
    def strict_basic(self) -> bool:
        """Is this card one of the five basic lands (not Snow or Wastes)."""
        return self.name in STRICT_BASICS

    @property
    def printings(self):
        """List of all printings of this card."""
        return self.cdb.card_name_to_printings[self.name]

    def __str__(self) -> str:
        return 'Card: {card.name}'.format(card=self)

    def __repr__(self) -> str:
        return '<Card: {card.name}>'.format(card=self)


class CardPrinting:
    """Model for storing information about card printings."""

    __slots__ = ('cdb', 'id_', 'card_name', 'set_code', 'set_number',
                 'set_integer', 'set_variant', 'multiverseid', 'artist',
                 'counts')

    def __init__(self, card_db, set_code, card_data):
        self.cdb = weakref.proxy(card_db)
        self.id_ = card_data['id']
        self.card_name = card_data['name']
        self.set_code = set_code
        self.set_number = card_data.get('number')
        self.multiverseid = card_data.get('multiverseid')
        self.artist = card_data['artist']

        if self.set_number is None:
            self.set_integer = None  # type: int
            self.set_variant = None  # type: str
        else:
            self.set_integer = int(self.set_number.strip(VARIANT_CHARS))
            self.set_variant = self.set_number.strip(string.digits) or None

    @property
    def card(self):
        """The Card associated with this printing."""
        return self.cdb.name_to_card[self.card_name]

    @property
    def set(self):
        """The CardSet associated with this printing."""
        return self.cdb.code_to_card_set[self.set_code]

    def __str__(self):
        return 'CardPrinting: {print.id_}'.format(print=self)

    def __repr__(self):
        return '<CardPrinting: {print.id_}>'.format(print=self)

    def __hash__(self):
        return hash(self.id_)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id_ == other.id_


class CardSet:
    """Model for storing card set information."""

    __slots__ = ('cdb', 'code', 'name', 'block', 'release_date',
                 'type_', 'online_only')

    def __init__(self, card_db, set_data):
        self.cdb = weakref.proxy(card_db)
        self.code = set_data['code']
        self.name = set_data['name']
        self.block = set_data.get('block')
        self.release_date = dt.datetime.strptime(
            set_data['releaseDate'], '%Y-%m-%d').date()
        self.type_ = set_data['type']
        self.online_only = set_data.get('onlineOnly', False)

    @property
    def printings(self):
        """The printings in this set.

        Note:
            Printings are ordered by set_integer, set_variant, multiverseid,
            card_name.
        """
        return self.cdb.set_code_to_printings[self.code]

    def printing_index(self, printing):
        """The index of a printing in a sets card list."""
        return self.cdb.set_code_to_printing_to_row[self.code][printing]

    def __str__(self):
        return 'CardSet: {cset.name}'.format(cset=self)

    def __repr__(self):
        return '<CardSet: {cset.code}>'.format(cset=self)
