"""pytest test configuration file."""

import time
from pathlib import Path
from typing import Dict, Generator, List
from uuid import UUID

import msgspec
import pytest
import responses

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall.models import ScryCard, ScryList, ScryMigration, ScrySet

TEST_DATA_DIR = Path(__file__).parent / "data"
SETS_DATA_FILE = TEST_DATA_DIR / "sets.json"
CARDS_DATA_FILE = TEST_DATA_DIR / "cards.json"
MIGRATIONS_DATA_FILE = TEST_DATA_DIR / "migrations.json"


@pytest.fixture(autouse=True)
def _set_timezone(monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    """Set timezone to UTC for testing."""
    try:
        with monkeypatch.context() as m:
            m.setenv("TZ", "UTC")
            time.tzset()
            yield
    finally:
        time.tzset()


@pytest.fixture(autouse=True)
def _fetcher_disable_cache() -> Generator[None, None, None]:
    """Patch fetcher cache dirs for testing."""
    with fetcher.SESSION.cache_disabled():
        yield


@pytest.fixture(autouse=True)
def requests_mock() -> Generator[responses.RequestsMock, None, None]:
    """Auto replace all requests with a mock."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def cards_data() -> List[ScryCard]:
    """Fixture containing all test card data."""
    with CARDS_DATA_FILE.open("rb") as card_data_file:
        return msgspec.json.decode(card_data_file.read(), type=List[ScryCard])


@pytest.fixture(scope="session")
def sets_data() -> List[ScrySet]:
    """Fixture containing all test set data."""
    with SETS_DATA_FILE.open("rb") as sets_data_file:
        sets_list = msgspec.json.decode(sets_data_file.read(), type=ScryList[ScrySet])
    return sets_list.data


@pytest.fixture(scope="session")
def migrations_data() -> List[ScryMigration]:
    """Fixture containing all test migrations data."""
    with MIGRATIONS_DATA_FILE.open("rb") as migrations_data_file:
        migrations_list = msgspec.json.decode(
            migrations_data_file.read(), type=ScryList[ScryMigration]
        )
    return migrations_list.data


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
