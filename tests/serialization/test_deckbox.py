"""Tests for mtg_ssm.serialization.deckbox"""

import os
import tempfile
import textwrap

import pytest

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts
from mtg_ssm.serialization import deckbox


@pytest.fixture
def cdb(sets_data):
    """card_db fixture for testing."""
    return card_db.CardDb(sets_data)


def test_get_deckbox_name(cdb):
    # Setup
    card_names = [
        'Chaotic Æther',
        'Delver of Secrets',
        'Insectile Aberration',
        'Boom',
        'Bust',
        'Bushi Tenderfoot',
        'Kenzo the Hardhearted',
        'Abattoir Ghoul',
    ]
    cards = [cdb.name_to_card[name] for name in card_names]
    # Execute
    deckbox_names = [deckbox.get_deckbox_name(card) for card in cards]
    # Verify
    expected = [
        'Chaotic Aether',
        'Delver of Secrets',
        None,
        'Boom // Bust',
        None,
        'Bushi Tenderfoot',
        None,
        'Abattoir Ghoul',
    ]
    assert deckbox_names == expected


def test_rfp(cdb):
    # Setup
    printing = cdb.id_to_printing['c08c564300a6a6d3f9c1c1dfbcab9351be3a04ae']
    print_counts = {printing: {
        counts.CountTypes.copies: 3,
        counts.CountTypes.foils: 5,
    }}
    # Execute
    rows = list(deckbox.rows_for_printing(printing, print_counts))
    # Verify
    expected = [
        {
            'Count': 3,
            'Tradelist Count': 0,
            'Name': 'Boom // Bust',
            'Edition': 'Planar Chaos',
            'Card Number': 112,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': None,
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': None,
            'Textless': None,
            'My Price': None,
        },
        {
            'Count': 5,
            'Tradelist Count': 0,
            'Name': 'Boom // Bust',
            'Edition': 'Planar Chaos',
            'Card Number': 112,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': 'foil',
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': None,
            'Textless': None,
            'My Price': None,
        },
    ]
    assert rows == expected


def test_rfp_split_second_half(cdb):
    # Setup
    printing = cdb.id_to_printing['2eecf5001fe332f5dadf4d87665bcf182c5f24ee']
    print_counts = {printing: {
        counts.CountTypes.copies: 3,
        counts.CountTypes.foils: 5,
    }}
    # Execute
    rows = list(deckbox.rows_for_printing(printing, print_counts))
    # Verify
    assert not rows


def test_rfp_promo(cdb):
    # Setup
    printing = cdb.id_to_printing['6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc']
    print_counts = {printing: {
        counts.CountTypes.copies: 0,
        counts.CountTypes.foils: 5,
    }}
    # Execute
    rows = list(deckbox.rows_for_printing(printing, print_counts))
    # Verify
    expected = [
        {
            'Count': 5,
            'Tradelist Count': 0,
            'Name': 'Black Sun\'s Zenith',
            'Edition': 'Magic Game Day Cards',
            'Card Number': 7,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': 'foil',
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': 'promo',
            'Textless': None,
            'My Price': None,
        },
    ]
    assert rows == expected


@pytest.mark.xfail
def test_alt_art_ertai(cdb):
    # Setup
    ertai1 = cdb.id_to_printing['08fcfee6a7c4eddcd44e43e918cbf9d479492fe7']
    ertai2 = cdb.id_to_printing['62ff415cafefac84a5bb7174cb7ef175c14625de']
    print_counts = {
        ertai1: {counts.CountTypes.foils: 5},
        ertai2: {counts.CountTypes.foils: 5},
    }
    # Execute
    ertai1_rows = list(deckbox.rows_for_printing(ertai1, print_counts))
    ertai2_rows = list(deckbox.rows_for_printing(ertai2, print_counts))
    # Verify
    assert ertai1_rows != ertai2_rows


def test_rows_from_print_counts(cdb):
    # Setup
    bust = cdb.id_to_printing['2eecf5001fe332f5dadf4d87665bcf182c5f24ee']
    boom = cdb.id_to_printing['c08c564300a6a6d3f9c1c1dfbcab9351be3a04ae']
    bsz = cdb.id_to_printing['6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc']
    print_counts = {
        bust: {
            counts.CountTypes.copies: 3,
            counts.CountTypes.foils: 5,
        },
        boom: {
            counts.CountTypes.copies: 7,
            counts.CountTypes.foils: 9,
        },
        bsz: {
            counts.CountTypes.foils: 11,
        }
    }
    # Execute
    rows = list(deckbox.deckbox_rows_from_print_counts(cdb, print_counts))
    # Verify
    expected = [
        {
            'Count': 7,
            'Tradelist Count': 0,
            'Name': 'Boom // Bust',
            'Edition': 'Planar Chaos',
            'Card Number': 112,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': None,
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': None,
            'Textless': None,
            'My Price': None,
        },
        {
            'Count': 9,
            'Tradelist Count': 0,
            'Name': 'Boom // Bust',
            'Edition': 'Planar Chaos',
            'Card Number': 112,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': 'foil',
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': None,
            'Textless': None,
            'My Price': None,
        },
        {
            'Count': 11,
            'Tradelist Count': 0,
            'Name': 'Black Sun\'s Zenith',
            'Edition': 'Magic Game Day Cards',
            'Card Number': 7,
            'Condition': 'Near Mint',
            'Language': 'English',
            'Foil': 'foil',
            'Signed': None,
            'Artist Proof': None,
            'Altered Art': None,
            'Misprint': None,
            'Promo': 'promo',
            'Textless': None,
            'My Price': None,
        },
    ]
    assert rows == expected


def test_create_counts_row(cdb):
    # Setup
    deckbox_rows = [
        {
            'Edition': 'Planechase 2012',
            'Count': '2',
            'Tradelist Count': '3',
            'Foil': 'foil',
            'Name': 'Foo // Bar',
            'Card Number': '12',
        },
        {
            'Edition': 'Innistrad',
            'Count': '4',
            'Tradelist Count': '0',
            'Foil': None,
            'Name': 'Thing',
            'Card Number': '95',
        },
    ]
    # Execute
    counts = [deckbox.create_counts_row(cdb, r) for r in deckbox_rows]
    # Verify
    expected = [
        {'name': 'Foo', 'set': 'PC2', 'number': '12', 'foils': 5},
        {'name': 'Thing', 'set': 'ISD', 'number': '95', 'copies': 4},
    ]
    assert counts == expected


def test_write(cdb):
    # Setup
    boom = cdb.id_to_printing['c08c564300a6a6d3f9c1c1dfbcab9351be3a04ae']
    bsz = cdb.id_to_printing['6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc']
    print_counts = {
        boom: {counts.CountTypes.copies: 1},
        bsz: {counts.CountTypes.foils: 3},
    }
    serializer = deckbox.MtgDeckboxSerializer(cdb)
    with tempfile.TemporaryDirectory() as tmpdirname:
        csvfilename = os.path.join(tmpdirname, 'outfile.csv')

        # Execute
        serializer.write(csvfilename, print_counts)

        # Verify
        with open(csvfilename, 'r') as csvfile:
            csvdata = csvfile.read()
    expected = textwrap.dedent("""\
        Count,Tradelist Count,Name,Edition,Card Number,Condition,Language,Foil,Signed,Artist Proof,Altered Art,Misprint,Promo,Textless,My Price
        1,0,Boom // Bust,Planar Chaos,112,Near Mint,English,,,,,,,,
        3,0,Black Sun's Zenith,Magic Game Day Cards,7,Near Mint,English,foil,,,,,promo,,
        """)
    assert csvdata == expected


def test_read(cdb):
    # Setup
    with tempfile.NamedTemporaryFile('w') as csvfile:
        csvfile.write(textwrap.dedent("""\
            Count,Tradelist Count,Name,Edition,Card Number,Condition,Language,Foil,Signed,Artist Proof,Altered Art,Misprint,Promo,Textless,My Price
            1,4,Boom // Bust,Planar Chaos,112,Near Mint,English,,,,,,,,
            3,8,Black Sun's Zenith,Magic Game Day Cards,7,Near Mint,English,foil,,,,,promo,,
            """))
        csvfile.flush()
        serializer = deckbox.MtgDeckboxSerializer(cdb)

        # Execute
        print_counts = serializer.read(csvfile.name)

    # Verify
    boom = cdb.id_to_printing['c08c564300a6a6d3f9c1c1dfbcab9351be3a04ae']
    bsz = cdb.id_to_printing['6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc']
    assert print_counts == {
        boom: {counts.CountTypes.copies: 5},
        bsz: {counts.CountTypes.foils: 11},
    }
