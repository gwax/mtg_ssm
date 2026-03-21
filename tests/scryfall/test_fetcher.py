"""Tests for mtg_ssm.scryfall.fetcher."""

import re
from pathlib import Path
from re import Pattern

import pytest
from responses import RequestsMock, matchers

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall.models import ScryCard, ScryMigration, ScrySet
from tests import gen_testdata

BULK_CARDS_REGEX = r"https://data\.scryfall\.io/default-cards/default-cards-\d{14}\.json"

ENDPOINT_TO_FILE: dict[str | Pattern[str], Path] = {
    fetcher.BULK_DATA_ENDPOINT: gen_testdata.TARGET_BULK_FILE,
    fetcher.SETS_ENDPOINT: gen_testdata.TARGET_SETS_FILE1,
    gen_testdata.SETS_NEXTPAGE_URL: gen_testdata.TARGET_SETS_FILE2,
    fetcher.MIGRATIONS_ENDPOINT: gen_testdata.TARGET_MIGRATIONS_FILE,
    re.compile(BULK_CARDS_REGEX): gen_testdata.TARGET_CARDS_FILE,
}


@pytest.fixture
def _scryurls(requests_mock: RequestsMock) -> None:
    """Populate mock responses for scryfall urls."""
    for endpoint, filename in ENDPOINT_TO_FILE.items():
        with filename.open("rb") as endpoint_file:
            matcher_list = []
            if isinstance(endpoint, str):
                matcher_list.append(matchers.query_string_matcher(endpoint.partition("?")[2]))
            requests_mock.add(
                "GET",
                endpoint,
                status=200,
                content_type="application/json",
                body=endpoint_file.read(),
                match=matcher_list,
            )


@pytest.mark.usefixtures("_scryurls")
def test_scryfetch() -> None:
    scrydata1 = fetcher.scryfetch()
    scrydata2 = fetcher.scryfetch()
    assert scrydata1 == scrydata2
    assert {s.code for s in scrydata1.sets} == gen_testdata.TEST_SETS_TO_CARDS.keys()
    assert {(c.set, c.name) for c in scrydata1.cards} == {
        (key, card) for key, value in gen_testdata.TEST_SETS_TO_CARDS.items() for card in value
    }


@pytest.mark.usefixtures("_scryurls")
def test_data_fixtures(
    scryfall_data: ScryfallDataSet,
    sets_data: list[ScrySet],
    cards_data: list[ScryCard],
    migrations_data: list[ScryMigration],
) -> None:
    scrydata = fetcher.scryfetch()
    assert scrydata == scryfall_data
    assert scrydata.sets == sets_data
    assert scrydata.cards == cards_data
    assert scrydata.migrations == migrations_data
