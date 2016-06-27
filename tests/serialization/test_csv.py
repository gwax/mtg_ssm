"""Tests for mtg_ssm.serialization.csv."""

import os
import tempfile
import textwrap

import pytest

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import models
from mtg_ssm.serialization import csv

TEST_PRINT_ID = 'fc46a4b72d216117a352f59217a84d0baeaaacb7'


@pytest.fixture
def cdb(sets_data):
    """card_db fixture for testing."""
    sets_data = {k: v for k, v in sets_data.items() if k in {'MMA', 'pMGD'}}
    return card_db.CardDb(sets_data)


@pytest.fixture
def printing(cdb):
    """Printing fixture for testing."""
    return cdb.id_to_printing[TEST_PRINT_ID]


def test_header():
    # Verify
    expected = [
        'set',
        'name',
        'number',
        'multiverseid',
        'id',
        'copies',
        'foils',
    ]
    assert csv.CSV_HEADER == expected


def test_row_for_printing(printing):
    print_counts = {printing: {
        models.CountTypes.copies: 3,
        models.CountTypes.foils: 5,
    }}
    # Execute
    csv_row = csv.row_for_printing(printing, print_counts)
    # Verify
    expected = {
        'set': 'MMA',
        'name': 'Thallid',
        'number': '167',
        'multiverseid': 370352,
        'id': 'fc46a4b72d216117a352f59217a84d0baeaaacb7',
        'copies': 3,
        'foils': 5,
    }
    assert csv_row == expected


def test_rows_for_printings(cdb):
    # Execute
    row_generator = csv.rows_for_printings(cdb, {})
    # Verify
    rows = list(row_generator)
    expected = [
        {
            'set': 'pMGD',
            'name': "Black Sun's Zenith",
            'number': '7',
            'multiverseid': None,
            'id': '6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc',
        },
        {
            'set': 'MMA',
            'name': 'Thallid',
            'number': '167',
            'multiverseid': 370352,
            'id': 'fc46a4b72d216117a352f59217a84d0baeaaacb7',
        },
    ]
    assert rows == expected


def test_write(cdb, printing):
    # Setup
    print_counts = {printing: {
        models.CountTypes.copies: 1,
        models.CountTypes.foils: 12,
    }}
    serializer = csv.MtgCsvSerializer(cdb)
    with tempfile.TemporaryDirectory() as tmpdirname:
        csvfilename = os.path.join(tmpdirname, 'outfile.csv')

        # Execute
        serializer.write(csvfilename, print_counts)

        # Verify
        with open(csvfilename, 'r') as csvfile:
            csvdata = csvfile.read()
    expected = textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,1,12
        """)
    assert csvdata == expected


def test_read(cdb, printing):
    # Setup
    with tempfile.NamedTemporaryFile('w') as csvfile:
        csvfile.write(textwrap.dedent("""\
            set,name,number,multiverseid,id,copies,foils
            MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,3,72
            """))
        csvfile.flush()
        serializer = csv.MtgCsvSerializer(cdb)

        # Execute
        print_counts = serializer.read(csvfile.name)

    # Verify
    assert print_counts == {printing: {
        models.CountTypes.copies: 3,
        models.CountTypes.foils: 72,
    }}
