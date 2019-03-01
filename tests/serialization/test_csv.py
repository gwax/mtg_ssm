"""Tests for mtg_ssm.serialization.csv."""
# pylint: disable=redefined-outer-name

from pathlib import Path
import textwrap
from typing import Dict
from uuid import UUID

from mtg_ssm.containers import counts
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.counts import ScryfallCardCount
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.serialization import csv

TEST_CARD_ID = UUID("57f25ead-b3ec-4c40-972d-d750ed2f5319")


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
    card_counts = {counts.CountType.nonfoil: 3, counts.CountType.foil: 5}
    csv_row = csv.row_for_card(card, card_counts)
    assert csv_row == {
        "set": "phop",
        "name": "Stairs to Infinity",
        "collector_number": "P1",
        "scryfall_id": TEST_CARD_ID,
        "nonfoil": 3,
        "foil": 5,
    }


def test_rows_for_cards_verbose(
    scryfall_data: ScryfallDataSet, id_to_card: Dict[UUID, ScryCard]
) -> None:
    cards = [
        id_to_card[TEST_CARD_ID],
        id_to_card[UUID("dd88131a-2811-4a1f-bb9a-c82e12c1493b")],
    ]
    card_counts: ScryfallCardCount = {TEST_CARD_ID: {counts.CountType.nonfoil: 3}}
    collection = MagicCollection(
        oracle=Oracle(ScryfallDataSet(cards=cards, sets=scryfall_data.sets)),
        counts=card_counts,
    )
    rows = csv.rows_for_cards(collection, True)
    assert list(rows) == [
        {
            "set": "phop",
            "name": "Stairs to Infinity",
            "collector_number": "P1",
            "scryfall_id": TEST_CARD_ID,
            "nonfoil": 3,
        },
        {
            "set": "pmbs",
            "name": "Black Sun's Zenith",
            "collector_number": "39",
            "scryfall_id": UUID("dd88131a-2811-4a1f-bb9a-c82e12c1493b"),
        },
    ]


def test_rows_for_cards_terse(scryfall_data: ScryfallDataSet) -> None:
    card_counts: counts.ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.nonfoil: 3}
    }
    collection = MagicCollection(oracle=Oracle(scryfall_data), counts=card_counts)
    rows = csv.rows_for_cards(collection, False)
    assert list(rows) == [
        {
            "set": "phop",
            "name": "Stairs to Infinity",
            "collector_number": "P1",
            "scryfall_id": TEST_CARD_ID,
            "nonfoil": 3,
        }
    ]


def test_write_verbose(
    scryfall_data: ScryfallDataSet, id_to_card: Dict[UUID, ScryCard], tmp_path: Path
) -> None:
    csv_path = tmp_path / "outfile.csv"
    cards = [
        id_to_card[TEST_CARD_ID],
        id_to_card[UUID("dd88131a-2811-4a1f-bb9a-c82e12c1493b")],
    ]
    card_counts: ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.nonfoil: 3, counts.CountType.foil: 7}
    }
    collection = MagicCollection(
        oracle=Oracle(ScryfallDataSet(cards=cards, sets=scryfall_data.sets)),
        counts=card_counts,
    )
    serializer = csv.CsvFullDialect()
    serializer.write(csv_path, collection)
    with csv_path.open("rt") as csv_file:
        assert csv_file.read() == textwrap.dedent(
            """\
            set,name,collector_number,scryfall_id,nonfoil,foil
            phop,Stairs to Infinity,P1,57f25ead-b3ec-4c40-972d-d750ed2f5319,3,7
            pmbs,Black Sun\'s Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,,
            """
        )


def test_write_terse(scryfall_data: ScryfallDataSet, tmp_path: Path) -> None:
    csv_path = tmp_path / "outfile.csv"
    card_counts: counts.ScryfallCardCount = {
        TEST_CARD_ID: {counts.CountType.nonfoil: 3}
    }
    collection = MagicCollection(oracle=Oracle(scryfall_data), counts=card_counts)

    serializer = csv.CsvTerseDialect()
    serializer.write(csv_path, collection)
    with csv_path.open("rt") as csv_file:
        assert csv_file.read() == textwrap.dedent(
            """\
            set,name,collector_number,scryfall_id,nonfoil,foil
            phop,Stairs to Infinity,P1,57f25ead-b3ec-4c40-972d-d750ed2f5319,3,
            """
        )


def test_read(scryfall_data: ScryfallDataSet, tmp_path: Path) -> None:
    csv_path = tmp_path / "infile.csv"
    oracle = Oracle(scryfall_data)
    with csv_path.open("wt") as csv_file:
        csv_file.write(
            textwrap.dedent(
                """\
                set,name,collector_number,scryfall_id,nonfoil,foil
                phop,Stairs to Infinity,P1,57f25ead-b3ec-4c40-972d-d750ed2f5319,3,7
                """
            )
        )
    serializer = csv.CsvFullDialect()
    collection = serializer.read(csv_path, oracle)
    assert collection.counts == {
        TEST_CARD_ID: {counts.CountType.nonfoil: 3, counts.CountType.foil: 7}
    }
