"""Scryfall data fetcher."""

import gzip
import os
from typing import List, cast

import appdirs
import msgspec
from requests_cache import CachedSession, SerializerPipeline, Stage, pickle_serializer

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import (
    ScryBulkData,
    ScryCard,
    ScryList,
    ScryMigration,
    ScrySet,
)

APP_AUTHOR = "gwax"
APP_NAME = "mtg_ssm"
CACHE_DIR = appdirs.user_cache_dir(APP_NAME, APP_AUTHOR)
CACHE_SERIALIZER = SerializerPipeline(
    [
        pickle_serializer,
        Stage(dumps=gzip.compress, loads=gzip.decompress),
    ],
    is_binary=True,
)
SESSION = CachedSession(
    os.path.join(CACHE_DIR, "requests_cache.sqlite"),
    backend="sqlite",
    serializer=CACHE_SERIALIZER,
    cache_control=True,
    expire_after=86400,
)

BULK_DATA_ENDPOINT = "https://api.scryfall.com/bulk-data"
SETS_ENDPOINT = "https://api.scryfall.com/sets"
MIGRATIONS_ENDPOINT = "https://api.scryfall.com/migrations"
BULK_TYPE = "default_cards"

REQUESTS_TIMEOUT_SECONDS = 30


def _fetch_endpoint(endpoint: str) -> bytes:
    response = SESSION.get(endpoint)
    response.raise_for_status()
    cached_response = getattr(response, "from_cache", False)
    print(f'Fetched {endpoint}{" [CACHED]" if cached_response else ""}')
    return response.content


def scryfetch() -> ScryfallDataSet:  # pylint: disable=too-many-locals
    """Retrieve and deserialize Scryfall object data."""
    print("Reading data from scryfall")
    scrylist_decoder = msgspec.json.Decoder(ScryList)

    bulk_data_list = scrylist_decoder.decode(_fetch_endpoint(BULK_DATA_ENDPOINT))
    bulk_data = cast(List[ScryBulkData], bulk_data_list.data)

    sets_list = scrylist_decoder.decode(_fetch_endpoint(SETS_ENDPOINT))
    sets_data = cast(List[ScrySet], sets_list.data)
    while sets_list.has_more and sets_list.next_page is not None:
        sets_list = scrylist_decoder.decode(_fetch_endpoint(sets_list.next_page))
        sets_data += cast(List[ScrySet], sets_list.data)

    migrations_list = scrylist_decoder.decode(_fetch_endpoint(MIGRATIONS_ENDPOINT))
    migrations_data = cast(List[ScryMigration], migrations_list.data)
    while migrations_list.has_more and migrations_list.next_page is not None:
        migrations_list = scrylist_decoder.decode(
            _fetch_endpoint(migrations_list.next_page)
        )
        migrations_data += cast(List[ScryMigration], migrations_list.data)

    [cards_endpoint] = [bd.download_uri for bd in bulk_data if bd.type == BULK_TYPE]
    cards_data = msgspec.json.decode(
        _fetch_endpoint(cards_endpoint), type=List[ScryCard]
    )

    scryfall_data = ScryfallDataSet(
        sets=sets_data, cards=cards_data, migrations=migrations_data
    )
    return scryfall_data
