"""Tests for mtg_ssm.serialization.csv."""

import tempfile
import textwrap

import pytest

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts
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
    assert csv.CSV_HEADER == [
        'set',
        'name',
        'number',
        'multiverseid',
        'id',
        'copies',
        'foils',
    ]


def test_row_for_printing(printing):
    print_counts = {printing: {
        counts.CountTypes.copies: 3,
        counts.CountTypes.foils: 5,
    }}
    csv_row = csv.row_for_printing(printing, print_counts)
    assert csv_row == {
        'set': 'MMA',
        'name': 'Thallid',
        'number': '167',
        'multiverseid': 370352,
        'id': 'fc46a4b72d216117a352f59217a84d0baeaaacb7',
        'copies': 3,
        'foils': 5,
    }


def test_rows_for_printings(cdb):
    rows = csv.rows_for_printings(cdb, {})
    assert list(rows) == [
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


def test_write(cdb, printing):
    print_counts = {printing: {
        counts.CountTypes.copies: 1,
        counts.CountTypes.foils: 12,
    }}
    serializer = csv.MtgCsvSerializer(cdb)
    with tempfile.NamedTemporaryFile(mode='rt') as outfile:
        serializer.write(outfile.name, print_counts)
        csvdata = outfile.read()
    assert csvdata == textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,1,12
    """)


def test_read(cdb, printing):
    with tempfile.NamedTemporaryFile('w') as infile:
        infile.write(textwrap.dedent("""\
            set,name,number,multiverseid,id,copies,foils
            MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,3,72
        """))
        infile.flush()
        serializer = csv.MtgCsvSerializer(cdb)
        print_counts = serializer.read(infile.name)
    assert print_counts == {printing: {
        counts.CountTypes.copies: 3,
        counts.CountTypes.foils: 72,
    }}
