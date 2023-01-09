"""pytest test configuration file."""
# pylint: disable=redefined-outer-name

import json
from pathlib import Path
from typing import Dict, Generator, List
from uuid import UUID

import pytest
import responses
from _pytest.monkeypatch import MonkeyPatch

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import (
    ScryCard,
    ScryMigration,
    ScryObjectList,
    ScryRootList,
    ScrySet,
)

TEST_DATA_DIR = Path(__file__).parent / "data"
SETS_DATA_FILE = TEST_DATA_DIR / "sets.json"
CARDS_DATA_FILE = TEST_DATA_DIR / "cards.json"
MIGRATIONS_DATA_FILE = TEST_DATA_DIR / "migrations.json"


@pytest.fixture(autouse=True)
def fetcher_cache_dir(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    """Patch fetcher cache dirs for testing."""
    cache_path = tmp_path / "cache"
    monkeypatch.setattr("mtg_ssm.scryfall.fetcher.CACHE_DIR", cache_path)
    return cache_path


@pytest.fixture(autouse=True)
def requests_mock() -> Generator[responses.RequestsMock, None, None]:
    """Auto replace all requests with a mock."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def cards_data() -> List[ScryCard]:
    """Fixture containing all test card data."""
    with CARDS_DATA_FILE.open("rt", encoding="utf-8") as card_data_file:
        card_json = json.load(card_data_file)
    return ScryRootList[ScryCard].parse_obj(card_json).__root__


@pytest.fixture(scope="session")
def sets_data() -> List[ScrySet]:
    """Fixture containing all test set data."""
    with SETS_DATA_FILE.open("rt", encoding="utf-8") as sets_data_file:
        sets_json = json.load(sets_data_file)
    return ScryObjectList[ScrySet].parse_obj(sets_json).data


@pytest.fixture(scope="session")
def migrations_data() -> List[ScryMigration]:
    """Fixture containing all test migrations data."""
    with MIGRATIONS_DATA_FILE.open("rt", encoding="utf-8") as migrations_data_file:
        migrations_json = json.load(migrations_data_file)
    return ScryObjectList[ScryMigration].parse_obj(migrations_json).data


@pytest.fixture(scope="session")
def id_to_card(cards_data: List[ScryCard]) -> Dict[UUID, ScryCard]:
    """Fixture returning scryfall id to card object for all test card data."""
    return {card.id: card for card in cards_data}


@pytest.fixture(scope="session")
def scryfall_data(
    cards_data: List[ScryCard],
    sets_data: List[ScrySet],
    migrations_data: List[ScryMigration],
) -> ScryfallDataSet:
    """Fixture containing all scryfall test data."""
    return ScryfallDataSet(sets=sets_data, cards=cards_data, migrations=migrations_data)
