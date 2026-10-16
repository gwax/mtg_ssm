"""Tests for mtg_ssm.scryfall.fetcher."""

import gzip
import re
from pathlib import Path
from re import Pattern

import msgspec
import pytest
from responses import RequestsMock, matchers

import mtg_ssm
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall.models import ScryCard, ScryMigration, ScrySet
from tests import gen_testdata

BULK_CARDS_REGEX = (
    r"https://data\.scryfall\.io/default-cards/default-cards-\d{14}\.json(?:l\.gz)?$"
)

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
    bulk = msgspec.json.decode(gen_testdata.TARGET_BULK_FILE.read_bytes())["data"][0]
    for endpoint, filename in ENDPOINT_TO_FILE.items():
        with filename.open("rb") as endpoint_file:
            matcher_list = [
                matchers.header_matcher(
                    {
                        "User-Agent": f"mtg-ssm/{mtg_ssm.__version__} (https://github.com/gwax/mtg_ssm)",
                        "Accept": "application/json;q=0.9,*/*;q=0.8",
                    }
                )
            ]
            if isinstance(endpoint, str):
                matcher_list.append(matchers.query_string_matcher(endpoint.partition("?")[2]))
            body = endpoint_file.read()
            if filename == gen_testdata.TARGET_CARDS_FILE and bulk.get("jsonl_download_uri"):
                body = gzip.compress(
                    b"\n".join(msgspec.json.encode(card) for card in msgspec.json.decode(body))
                )
            requests_mock.add(
                "GET",
                endpoint,
                status=200,
                content_type="application/json",
                body=body,
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


@pytest.mark.usefixtures("_scryurls")
@pytest.mark.parametrize("encoding", ["gzip-file", "gzip-http", "plain"])
def test_scryfetch_jsonl(
    requests_mock: RequestsMock, scryfall_data: ScryfallDataSet, encoding: str
) -> None:
    bulk = msgspec.json.decode(gen_testdata.TARGET_BULK_FILE.read_bytes())
    download_uri = bulk["data"][0].pop("download_uri", None)
    if download_uri is not None:
        download_uri = download_uri.replace(".json", ".jsonl.gz")
    else:
        download_uri = bulk["data"][0]["jsonl_download_uri"]
    bulk["data"][0]["jsonl_download_uri"] = download_uri
    bulk["data"][0].pop("content_type", None)
    bulk["data"][0].pop("content_encoding", None)
    requests_mock.replace("GET", fetcher.BULK_DATA_ENDPOINT, json=bulk)
    requests_mock.remove("GET", re.compile(BULK_CARDS_REGEX))

    # Include blank lines and a final record without a trailing newline.
    body = b"\n\n".join(msgspec.json.encode(card) for card in scryfall_data.cards)
    headers = {}
    if encoding != "plain":
        body = gzip.compress(body)
    if encoding == "gzip-http":
        headers["Content-Encoding"] = "gzip"
    requests_mock.add(
        "GET", download_uri, body=body, content_type="application/gzip", headers=headers
    )

    assert fetcher.scryfetch() == scryfall_data
