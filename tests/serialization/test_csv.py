"""Tests for mtg_ssm.serialization.csv."""
# pylint: disable=redefined-outer-name

import textwrap
from pathlib import Path
from typing import Dict
from uuid import UUID

import pytest
from pytest_snapshot.plugin import Snapshot

from mtg_ssm.containers import counts
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.counts import ScryfallCardCount
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.serialization import csv

TEST_CARD_ID = UUID("57f25ead-b3ec-4c40-972d-d750ed2f5319")


@pytest.fixture(scope="session")
def oracle(scryfall_data: ScryfallDataSet) -> Oracle:
    """Test fixture Oracle with limited data."""
    accepted_sets = {"phop", "pmbs"}
    scryfall_data2 = ScryfallDataSet(
        sets=[s for s in scryfall_data.sets if s.code in accepted_sets],
        cards=[c for c in scryfall_data.cards if c.set in accepted_sets],
        migrations=[],
    )
    return Oracle(scryfall_data2)


def test_header() -> None:
    assert csv.CSV_HEADER == [
        "set",
        "name",
        "collector_number",
        "scryfall_id",
        "nonfoil",
        "foil",
    ]


def test_row_for_card(id_to_card: Dict[UUID, ScryCard]) -> None:
    card = id_to_card[TEST_CARD_ID]
    card_counts = {counts.CountType.NONFOIL: 3, counts.CountType.FOIL: 5}
    csv_row = csv.row_for_card(card, card_counts)
    assert csv_row == {
        "set": "PHOP",
        "name": "Stairs to Infinity",
        "collector_number": "P1",
        "scryfall_id": TEST_CARD_ID,
        "nonfoil": 3,
        "foil": 5,
    }


def test_rows_for_cards_verbose(oracle: Oracle) -> None:
    card_counts: ScryfallCardCount = {TEST_CARD_ID: {counts.CountType.NONFOIL: 3}}
    collection = MagicCollection(oracle=oracle, counts=card_counts)
    rows = csv.rows_for_cards(collection, True)
    assert list(rows) == [
        {
            "set": "PHOP",
            "name": "Stairs to Infinity",
            "collector_number": "P1",
            "scryfall_id": TEST_CARD_ID,
            "nonfoil": 3,
        },
        {
            "collector_number": "41",
            "name": "Tazeem",
            "scryfall_id": UUID("76e5383d-ac12-4abc-aa30-15e99ded2d6f"),
            "set": "PHOP",
        },
        {
            "set": "PMBS",
            "name": "Hero of Bladehold",
            "collector_number": "8★",
            "scryfall_id": UUID("8829efa0-498a-43ca-91aa-f9caeeafe298"),
        },
        {
            "set": "PMBS",
            "name": "Black Sun's Zenith",
            "collector_number": "39",
            "scryfall_id": UUID("dd88131a-2811-4a1f-bb9a-c82e12c1493b"),
        },
    ]


def test_rows_for_cards_terse(oracle: Oracle) -> None:
    card_counts: counts.ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.NONFOIL: 3}
    }
    collection = MagicCollection(oracle=oracle, counts=card_counts)
    rows = csv.rows_for_cards(collection, False)
    assert list(rows) == [
        {
            "set": "PHOP",
            "name": "Stairs to Infinity",
            "collector_number": "P1",
            "scryfall_id": TEST_CARD_ID,
            "nonfoil": 3,
        }
    ]


def test_write_verbose(snapshot: Snapshot, oracle: Oracle, tmp_path: Path) -> None:
    csv_path = tmp_path / "outfile.csv"
    card_counts: ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.NONFOIL: 3, counts.CountType.FOIL: 7}
    }
    collection = MagicCollection(oracle=oracle, counts=card_counts)
    serializer = csv.CsvFullDialect()
    serializer.write(csv_path, collection)
    with csv_path.open("rt", encoding="utf-8") as csv_file:
        snapshot.assert_match(csv_file.read(), "collection.csv")


def test_write_terse(snapshot: Snapshot, oracle: Oracle, tmp_path: Path) -> None:
    csv_path = tmp_path / "outfile.csv"
    card_counts: counts.ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.NONFOIL: 3}
    }
    collection = MagicCollection(oracle=oracle, counts=card_counts)

    serializer = csv.CsvTerseDialect()
    serializer.write(csv_path, collection)
    with csv_path.open("rt", encoding="utf-8") as csv_file:
        snapshot.assert_match(csv_file.read(), "collection.csv")


def test_read(oracle: Oracle, tmp_path: Path) -> None:
    csv_path = tmp_path / "infile.csv"
    with csv_path.open("wt", encoding="utf-8") as csv_file:
        csv_file.write(
            textwrap.dedent(
                """\
                set,name,collector_number,scryfall_id,nonfoil,foil
                PHOP,Stairs to Infinity,P1,57f25ead-b3ec-4c40-972d-d750ed2f5319,3,7
                """
            )
        )
    serializer = csv.CsvFullDialect()
    collection = serializer.read(csv_path, oracle)
    assert collection.counts == {
        TEST_CARD_ID: {counts.CountType.NONFOIL: 3, counts.CountType.FOIL: 7}
    }
