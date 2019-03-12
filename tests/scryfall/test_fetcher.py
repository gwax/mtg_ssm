"""Tests for mtg_ssm.scryfall.fetcher."""
# pylint: disable=protected-access

import gzip
import pickle
from typing import List

import pytest
from responses import RequestsMock

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet
from tests import gen_testdata

ENDPOINT_TO_FILE = {
    fetcher.BULK_DATA_ENDPOINT: gen_testdata.TARGET_BULK_FILE,
    fetcher.SETS_ENDPOINT: gen_testdata.TARGET_SETS_FILE1,
    gen_testdata.SETS_NEXTPAGE_URL: gen_testdata.TARGET_SETS_FILE2,
    "https://archive.scryfall.com/json/scryfall-default-cards.json": gen_testdata.TARGET_CARDS_FILE,
}


@pytest.fixture
def scryurls(requests_mock: RequestsMock) -> None:
    """Populate mock responses for scryfall urls."""
    for endpoint, filename in ENDPOINT_TO_FILE.items():
        with open(filename, "rb") as endpoint_file:
            requests_mock.add(
                "GET",
                endpoint,
                status=200,
                content_type="application/json",
                body=endpoint_file.read(),
                match_querystring=True,
            )


@pytest.mark.usefixtures("scryurls")
def test_scryfetch() -> None:
    scrydata1 = fetcher.scryfetch()
    scrydata2 = fetcher.scryfetch()
    assert scrydata1 == scrydata2
    assert {s.code for s in scrydata1.sets} == gen_testdata.TEST_SETS_TO_CARDS.keys()
    assert {(c.set, c.name) for c in scrydata1.cards} == {
        (key, card)
        for key, value in gen_testdata.TEST_SETS_TO_CARDS.items()
        for card in value
    }


@pytest.mark.parametrize(
    "baddata",
    [
        pytest.param(b"garbage", id="not gzipped"),
        pytest.param(gzip.compress(b"garbage"), id="not pickled"),
        pytest.param(gzip.compress(pickle.dumps("garbage")), id="not scrydata"),
    ],
)
@pytest.mark.usefixtures("scryurls")
def test_break_object_cache(baddata: bytes) -> None:
    scrydata1 = fetcher.scryfetch()
    with open(fetcher._cache_path(fetcher.OBJECT_CACHE_URL), "wb") as cache_file:
        cache_file.write(baddata)
    scrydata2 = fetcher.scryfetch()
    assert scrydata1 == scrydata2


@pytest.mark.usefixtures("scryurls")
def test_data_fixtures(
    scryfall_data: ScryfallDataSet, sets_data: List[ScrySet], cards_data: List[ScryCard]
) -> None:
    scrydata = fetcher.scryfetch()
    assert scrydata == scryfall_data
    assert scrydata.sets == sets_data
    assert scrydata.cards == cards_data
