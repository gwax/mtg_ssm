"""Scryfall data fetcher."""

import gzip
import json
import os
import pickle
import pprint
import uuid
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Mapping, Union, cast

import appdirs
import requests
from pydantic import ValidationError

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import (
    ScryBulkData,
    ScryCard,
    ScryMigration,
    ScryObjectList,
    ScrySet,
)

DEBUG = 0
try:
    DEBUG = int(os.getenv("DEBUG", "0"))
except ValueError:
    pass

APP_AUTHOR = "gwax"
APP_NAME = "mtg_ssm"
CACHE_DIR = Path(appdirs.user_cache_dir(APP_NAME, APP_AUTHOR))

BULK_DATA_ENDPOINT = "https://api.scryfall.com/bulk-data"
SETS_ENDPOINT = "https://api.scryfall.com/sets"
MIGRATIONS_ENDPOINT = "https://api.scryfall.com/migrations"
BULK_TYPE = "default_cards"
OBJECT_CACHE_URL = "file:///$CACHE/pickled_object?v2"

CHUNK_SIZE = 8 * 1024 * 1024
DESERIALIZE_BATCH_SIZE = 50
REQUESTS_TIMEOUT_SECONDS = 10

JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]


def _value_from_validation_error(data: JSON, verr: ValidationError) -> Dict[str, Any]:
    values = {}
    for error in verr.errors():
        loc = error["loc"]
        value = data
        for field in loc:
            if field == "__root__":
                break
            if isinstance(value, Mapping) and isinstance(field, str):
                value = value[field]
            if isinstance(value, List) and isinstance(field, int):
                value = value[field]
        values[".".join([str(location) for location in loc])] = value
    return values


def _cache_path(endpoint: str, extension: str) -> Path:
    if not extension.startswith("."):
        extension = "." + extension
    cache_id = uuid.uuid5(uuid.NAMESPACE_URL, endpoint)
    return CACHE_DIR / f"{cache_id}{extension}"


def _fetch_endpoint(endpoint: str, *, dirty: bool, write_cache: bool = True) -> JSON:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _cache_path(endpoint, ".json.gz")
    if not cache_path.exists():
        dirty = True
    if dirty:
        print(f"Fetching {endpoint}")
        response = requests.get(endpoint, stream=True, timeout=REQUESTS_TIMEOUT_SECONDS)
        response.raise_for_status()
        if not write_cache:
            return response.json()
        print(f"Caching {endpoint}")
        with gzip.open(cache_path, "wb", compresslevel=1) as cache_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                cache_file.write(chunk)
    else:
        print(f"Reading cached {endpoint}")

    with gzip.open(cache_path, "rt", encoding="utf-8") as cache_file:
        return json.load(cache_file)


def _deserialize_cards(card_jsons: List[JSON]) -> List[ScryCard]:
    cards_data: List[ScryCard]
    if DEBUG:
        print("Process pool disabled")
        cards_data = []
        for card_json in card_jsons:
            try:
                cards_data.append(ScryCard.parse_obj(card_json))
            except ValidationError as err:
                print("Failed with pydantic errors on values:")
                pprint.pp(_value_from_validation_error(card_json, err))
                print("Failed on:")
                pprint.pp(card_json)
                raise
            except Exception:
                print("Failed on:")
                pprint.pp(card_json)
                raise
    else:
        with ProcessPoolExecutor() as executor:
            cards_futures = executor.map(
                ScryCard.parse_obj, card_jsons, chunksize=DESERIALIZE_BATCH_SIZE
            )
            cards_data = list(cards_futures)
    return cards_data


def scryfetch() -> ScryfallDataSet:  # pylint: disable=too-many-locals
    """Retrieve and deserialize Scryfall object data."""
    cached_bulk_json = None
    if _cache_path(BULK_DATA_ENDPOINT, ".json.gz").exists():
        cached_bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=False)
    bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=True, write_cache=False)
    cache_dirty = bulk_json != cached_bulk_json

    object_cache_path = _cache_path(OBJECT_CACHE_URL, ".pickle.gz")
    if object_cache_path.exists():
        if cache_dirty or DEBUG:
            object_cache_path.unlink()
        else:
            print("Loading cached scryfall data objects")
            try:
                with gzip.open(object_cache_path, "rb") as object_cache:
                    loaded_data = pickle.load(object_cache)
            except (OSError, pickle.UnpicklingError):
                pass
            else:
                if isinstance(loaded_data, ScryfallDataSet):
                    return loaded_data
            print("Error reading object cache, falling back")

    sets_list = ScryObjectList[ScrySet].parse_obj(
        _fetch_endpoint(SETS_ENDPOINT, dirty=cache_dirty)
    )
    sets_data = sets_list.data
    while sets_list.has_more and sets_list.next_page is not None:
        sets_list = ScryObjectList[ScrySet].parse_obj(
            _fetch_endpoint(sets_list.next_page, dirty=cache_dirty)
        )
        sets_data += sets_list.data

    migrations_list = ScryObjectList[ScryMigration].parse_obj(
        _fetch_endpoint(MIGRATIONS_ENDPOINT, dirty=cache_dirty)
    )
    migrations_data = migrations_list.data
    while migrations_list.has_more and migrations_list.next_page is not None:
        migrations_list = ScryObjectList[ScryMigration].parse_obj(
            _fetch_endpoint(migrations_list.next_page, dirty=cache_dirty)
        )
        migrations_data += migrations_list.data

    bulk_list = ScryObjectList[ScryBulkData].parse_obj(bulk_json)
    bulk_data = bulk_list.data
    [cards_endpoint] = [bd.download_uri for bd in bulk_data if bd.type == BULK_TYPE]

    cards_json = cast(List[JSON], _fetch_endpoint(cards_endpoint, dirty=cache_dirty))

    _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=cache_dirty, write_cache=True)

    print("Deserializing cards")
    cards_data = _deserialize_cards(cards_json)

    scryfall_data = ScryfallDataSet(
        sets=sets_data, cards=cards_data, migrations=migrations_data
    )
    with gzip.open(object_cache_path, "wb", compresslevel=1) as object_cache:
        pickle.dump(scryfall_data, object_cache, protocol=pickle.HIGHEST_PROTOCOL)
    return scryfall_data
