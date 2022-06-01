"""pytest test configuration file."""
# pylint: disable=redefined-outer-name

import json
import os
from typing import Dict, Generator, List, Sequence
from uuid import UUID

import pytest
import responses
from _pytest.monkeypatch import MonkeyPatch
from py._path.local import LocalPath

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import ScryCard, ScryObjectList, ScryRootList, ScrySet

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
def requests_mock() -> Generator[responses.RequestsMock, None, None]:
    """Auto replace all requests with a mock."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture(scope="session")
def cards_data() -> Sequence[ScryCard]:
    """Fixture containing all test card data."""
    with open(CARDS_DATA_FILE, "rt", encoding="utf-8") as card_data_file:
        card_json = json.load(card_data_file)
    return ScryRootList[ScryCard].parse_obj(card_json).__root__


@pytest.fixture(scope="session")
def sets_data() -> Sequence[ScrySet]:
    """Fixture containing all test set data."""
    with open(SETS_DATA_FILE, "rt", encoding="utf-8") as sets_data_file:
        sets_json = json.load(sets_data_file)
    return ScryObjectList[ScrySet].parse_obj(sets_json).data


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
