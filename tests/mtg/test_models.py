"""Tests for mtg_ssm.mtg.models"""

import datetime as dt

import pytest

from mtg_ssm.mtg import models


class Sentinel:
    """Simple sentinel object class."""

CARD_DB_SENTINEL = Sentinel()


def test_card(cards_data):
    ag_card_data = cards_data['958ae1416f8f6287115ccd7c5c61f2415a313546']
    card = models.Card(CARD_DB_SENTINEL, ag_card_data)
    assert card.cdb == CARD_DB_SENTINEL
    assert card.name == 'Abattoir Ghoul'
    assert not card.strict_basic


@pytest.mark.parametrize('name,id_,strict_basic', [
    ('Forest', 'c78d2da78c68c558b1adc734b3f164e885407ffc', True),
    ('Snow-Covered Forest', '5e9f08498a9343b1954103e493da2586be0fe394', False),
    ('Wastes', '68d4ca6db1b4f92aa306627cefa3d02137e4fa10', False),
    ('Abattoir Ghoul', '958ae1416f8f6287115ccd7c5c61f2415a313546', False),
])
def test_card_strict_basic(cards_data, name, id_, strict_basic):
    card = models.Card(CARD_DB_SENTINEL, cards_data[id_])
    assert card.name == name
    assert card.strict_basic is strict_basic


def test_card_printing(cards_data):
    ag_card_data = cards_data['958ae1416f8f6287115ccd7c5c61f2415a313546']
    printing = models.CardPrinting(CARD_DB_SENTINEL, 'ISD', ag_card_data)
    assert printing.cdb == CARD_DB_SENTINEL
    assert printing.id_ == '958ae1416f8f6287115ccd7c5c61f2415a313546'
    assert printing.card_name == 'Abattoir Ghoul'
    assert printing.set_code == 'ISD'
    assert printing.set_number == '85'
    assert printing.multiverseid == 222911
    assert printing.artist == 'Volkan Baga'
    assert printing.set_integer == 85
    assert printing.set_variant is None


@pytest.mark.parametrize('name,id_,num,nint,nvar', [
    # pylint: disable=line-too-long
    ('Delver of Secrets', '0b06d8d9e7662ada82bd29e1138d959978ba2280', '51a', 51, 'a'),
    ('Insectile Aberration', 'e5c4aa9a443c346ccbf8d99c9320138827065e05', '51b', 51, 'b'),
    ('Ertai, the Corrupted', '08fcfee6a7c4eddcd44e43e918cbf9d479492fe7', '107', 107, None),
    ('Ertai, the Corrupted', '62ff415cafefac84a5bb7174cb7ef175c14625de', '★107', 107, '★'),
])
def test_printing_variant(cards_data, name, id_, num, nint, nvar):
    printing = models.CardPrinting(CARD_DB_SENTINEL, None, cards_data[id_])
    assert printing.card_name == name
    assert printing.set_number == num
    assert printing.set_integer == nint
    assert printing.set_variant == nvar


def test_card_set(sets_data):
    # Setup
    set_data = sets_data['PLS']
    # Execute
    card_set = models.CardSet(CARD_DB_SENTINEL, set_data)
    # Verify
    assert card_set.cdb == CARD_DB_SENTINEL
    assert card_set.code == 'PLS'
    assert card_set.name == 'Planeshift'
    assert card_set.block == 'Invasion'
    assert card_set.release_date == dt.date(2001, 2, 5)
    assert card_set.type_ == 'expansion'
    assert not card_set.online_only
