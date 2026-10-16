"""Scryfall data fetcher."""

import gzip
import io
from pathlib import Path

import msgspec
from platformdirs import user_cache_dir
from requests_cache import CachedSession, SerializerPipeline, Stage, pickle_serializer

from mtg_ssm import __version__
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import ScryBulkData, ScryCard, ScryList, ScryMigration, ScrySet

APP_AUTHOR = "gwax"
APP_NAME = "mtg_ssm"
CACHE_DIR = Path(user_cache_dir(APP_NAME, APP_AUTHOR))
CACHE_SERIALIZER = SerializerPipeline(
    [
        pickle_serializer,
        Stage(dumps=gzip.compress, loads=gzip.decompress),
    ],
    is_binary=True,
)
SESSION = CachedSession(
    str(CACHE_DIR / "requests_cache.sqlite"),
    backend="sqlite",
    serializer=CACHE_SERIALIZER,
    cache_control=True,
    expire_after=86400,
)
SESSION.headers.update(
    {
        "User-Agent": f"mtg-ssm/{__version__} (https://github.com/gwax/mtg_ssm)",
        "Accept": "application/json;q=0.9,*/*;q=0.8",
    }
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


def _fetch_cards(bulk: ScryBulkData) -> list[ScryCard]:
    if bulk.jsonl_download_uri is not None:
        content = _fetch_endpoint(bulk.jsonl_download_uri)
        decoder = msgspec.json.Decoder(ScryCard)
        # Requests may already have decoded gzip supplied as an HTTP encoding.
        with (
            io.BytesIO(content) as stream,
            gzip.GzipFile(fileobj=stream) if content.startswith(b"\x1f\x8b") else stream as lines,
        ):
            return [decoder.decode(line) for line in lines if line.strip()]
    if bulk.download_uri is not None:
        return msgspec.json.decode(_fetch_endpoint(bulk.download_uri), type=list[ScryCard])
    msg = f"No download URI for Scryfall bulk data: {bulk.type}"
    raise ValueError(msg)


def scryfetch() -> ScryfallDataSet:
    """Retrieve and deserialize Scryfall object data."""
    print("Reading data from scryfall")
    bulk_data = msgspec.json.decode(
        _fetch_endpoint(BULK_DATA_ENDPOINT), type=ScryList[ScryBulkData]
    ).data

    scrylistset_decoder = msgspec.json.Decoder(ScryList[ScrySet])
    sets_list = scrylistset_decoder.decode(_fetch_endpoint(SETS_ENDPOINT))
    sets_data = sets_list.data
    while sets_list.has_more and sets_list.next_page is not None:
        sets_list = scrylistset_decoder.decode(_fetch_endpoint(sets_list.next_page))
        sets_data += sets_list.data

    scrylistmigration_decoder = msgspec.json.Decoder(ScryList[ScryMigration])
    migrations_list = scrylistmigration_decoder.decode(_fetch_endpoint(MIGRATIONS_ENDPOINT))
    migrations_data = migrations_list.data
    while migrations_list.has_more and migrations_list.next_page is not None:
        migrations_list = scrylistmigration_decoder.decode(
            _fetch_endpoint(migrations_list.next_page)
        )
        migrations_data += migrations_list.data

    [cards_bulk] = [bd for bd in bulk_data if bd.type == BULK_TYPE]
    cards_data = _fetch_cards(cards_bulk)

    return ScryfallDataSet(sets=sets_data, cards=cards_data, migrations=migrations_data)
