"""Tests for mtg_ssm.mtg.models"""

import datetime as dt

from mtg_ssm.mtg import models

CARD_DB_SENTINEL = object()


def test_card(cards_data):
    # Setup
    ag_card_data = cards_data['958ae1416f8f6287115ccd7c5c61f2415a313546']
    # Execute
    card = models.Card(CARD_DB_SENTINEL, ag_card_data)
    # Verify
    assert card.cdb is CARD_DB_SENTINEL
    assert card.name == 'Abattoir Ghoul'
    assert not card.strict_basic


def test_card_strict_basic(cards_data):
    # Setup
    forest_data = cards_data['c78d2da78c68c558b1adc734b3f164e885407ffc']
    snow_forest_data = cards_data['5e9f08498a9343b1954103e493da2586be0fe394']
    wastes_data = cards_data['68d4ca6db1b4f92aa306627cefa3d02137e4fa10']
    ag_card_data = cards_data['958ae1416f8f6287115ccd7c5c61f2415a313546']
    # Execute
    forest_card = models.Card(CARD_DB_SENTINEL, forest_data)
    snow_forest_card = models.Card(CARD_DB_SENTINEL, snow_forest_data)
    wastes_card = models.Card(CARD_DB_SENTINEL, wastes_data)
    ag_card = models.Card(CARD_DB_SENTINEL, ag_card_data)
    # Verify
    assert forest_card.name == 'Forest'
    assert forest_card.strict_basic
    assert snow_forest_card.name == 'Snow-Covered Forest'
    assert not snow_forest_card.strict_basic
    assert wastes_card.name == 'Wastes'
    assert not wastes_card.strict_basic
    assert ag_card.name == 'Abattoir Ghoul'
    assert not ag_card.strict_basic


def test_card_printing(cards_data):
    # Setup
    ag_card_data = cards_data['958ae1416f8f6287115ccd7c5c61f2415a313546']
    # Execute
    printing = models.CardPrinting(CARD_DB_SENTINEL, 'ISD', ag_card_data)
    # Verify
    assert printing.cdb is CARD_DB_SENTINEL
    assert printing.id_ == '958ae1416f8f6287115ccd7c5c61f2415a313546'
    assert printing.card_name == 'Abattoir Ghoul'
    assert printing.set_code == 'ISD'
    assert printing.set_number == '85'
    assert printing.multiverseid == 222911
    assert printing.artist == 'Volkan Baga'
    assert not printing.counts
    assert printing.set_integer == 85
    assert printing.set_variant is None


def test_printing_letter_var(cards_data):
    # Setup
    dlv_card_data = cards_data['0b06d8d9e7662ada82bd29e1138d959978ba2280']
    ia_card_data = cards_data['e5c4aa9a443c346ccbf8d99c9320138827065e05']
    # Execute
    dlv_printing = models.CardPrinting(
        CARD_DB_SENTINEL, 'ISD', dlv_card_data)
    ia_printing = models.CardPrinting(
        CARD_DB_SENTINEL, 'ISD', ia_card_data)
    # Verify
    assert dlv_printing.card_name == 'Delver of Secrets'
    assert ia_printing.card_name == 'Insectile Aberration'
    assert dlv_printing.set_number == '51a'
    assert ia_printing.set_number == '51b'
    assert dlv_printing.set_integer == 51
    assert ia_printing.set_integer == 51
    assert dlv_printing.set_variant == 'a'
    assert ia_printing.set_variant == 'b'


def test_printing_star_variant(cards_data):
    # Setup
    etc1_card_data = cards_data['08fcfee6a7c4eddcd44e43e918cbf9d479492fe7']
    etc2_card_data = cards_data['62ff415cafefac84a5bb7174cb7ef175c14625de']
    # Execut
    etc1_printing = models.CardPrinting(
        CARD_DB_SENTINEL, 'PLS', etc1_card_data)
    etc2_printing = models.CardPrinting(
        CARD_DB_SENTINEL, 'PLS', etc2_card_data)
    # Verify
    assert etc1_printing.card_name == 'Ertai, the Corrupted'
    assert etc2_printing.card_name == 'Ertai, the Corrupted'
    assert etc1_printing.set_number == '107'
    assert etc2_printing.set_number == '★107'
    assert etc1_printing.set_integer == 107
    assert etc2_printing.set_integer == 107
    assert etc1_printing.set_variant is None
    assert etc2_printing.set_variant == '★'


def test_card_set(sets_data):
    # Setup
    set_data = sets_data['PLS']
    # Execute
    card_set = models.CardSet(CARD_DB_SENTINEL, set_data)
    # Verify
    assert card_set.cdb is CARD_DB_SENTINEL
    assert card_set.code == 'PLS'
    assert card_set.name == 'Planeshift'
    assert card_set.block == 'Invasion'
    assert card_set.release_date == dt.date(2001, 2, 5)
    assert card_set.type_ == 'expansion'
    assert not card_set.online_only
