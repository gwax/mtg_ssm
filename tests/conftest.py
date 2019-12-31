"""pytest test configuration file."""
# pylint: disable=redefined-outer-name

import json
import os
from typing import Dict
from typing import List
from uuid import UUID

from _pytest.monkeypatch import MonkeyPatch
from py._path.local import LocalPath
import pytest
import responses

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet
from mtg_ssm.scryfall.schema import ScryfallUberSchema

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SETS_DATA_FILE = os.path.join(TEST_DATA_DIR, "sets.json")
CARDS_DATA_FILE = os.path.join(TEST_DATA_DIR, "cards.json")


@pytest.fixture(autouse=True)
def fetcher_cache_dir(tmpdir: LocalPath, monkeypatch: MonkeyPatch) -> LocalPath:
    """Patch fetcher cache dirs for testing."""
    cache_path = tmpdir.mkdir("cache")
    monkeypatch.setattr("mtg_ssm.scryfall.fetcher.CACHE_DIR", str(cache_path))
    return cache_path


@pytest.fixture(autouse=True)
def requests_mock() -> responses.RequestsMock:
    """Auto replace all requests with a mock."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def cards_data() -> List[ScryCard]:
    """Fixture containing all test card data."""
    schema = ScryfallUberSchema()
    with open(CARDS_DATA_FILE, "rt") as card_data_file:
        return [schema.load(c).data for c in json.load(card_data_file)]


@pytest.fixture(scope="session")
def sets_data() -> List[ScrySet]:
    """Fixture containing all test set data."""
    schema = ScryfallUberSchema()
    with open(SETS_DATA_FILE, "rt") as sets_data_file:
        return schema.load(json.load(sets_data_file)).data.data


@pytest.fixture(scope="session")
def id_to_card(cards_data: List[ScryCard]) -> Dict[UUID, ScryCard]:
    """Fixture returning scryfall id to card object for all test card data."""
    return {card.id: card for card in cards_data}


@pytest.fixture(scope="session")
def scryfall_data(
    cards_data: List[ScryCard], sets_data: List[ScrySet]
) -> ScryfallDataSet:
    """Fixture containing all scryfall test data."""
    return ScryfallDataSet(sets=sets_data, cards=cards_data)
