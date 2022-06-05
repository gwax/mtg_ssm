"""Scryfall data fetcher."""

import gzip
import json
import os
import pickle
import uuid
from concurrent.futures import ProcessPoolExecutor
from typing import Any, List, Mapping, Union, cast

import appdirs
import requests

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall.models import ScryBulkData, ScryCard, ScryObjectList, ScrySet

DEBUG = os.getenv("DEBUG", "0")

APP_AUTHOR = "gwax"
APP_NAME = "mtg_ssm"
CACHE_DIR = appdirs.user_cache_dir(APP_NAME, APP_AUTHOR)

BULK_DATA_ENDPOINT = "https://api.scryfall.com/bulk-data"
SETS_ENDPOINT = "https://api.scryfall.com/sets"
BULK_TYPE = "default_cards"
OBJECT_CACHE_URL = "file://$CACHE/pickled_object"

CHUNK_SIZE = 8 * 1024 * 1024
DESERIALIZE_BATCH_SIZE = 50

JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]


def _cache_path(endpoint: str, extension: str) -> str:
    if not extension.startswith("."):
        extension = "." + extension
    cache_id = uuid.uuid5(uuid.NAMESPACE_URL, endpoint)
    return os.path.join(CACHE_DIR, f"{cache_id}{extension}")


def _fetch_endpoint(endpoint: str, *, dirty: bool, write_cache: bool = True) -> JSON:
    print(f"Retrieving {endpoint}")
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = _cache_path(endpoint, ".json.gz")
    if not os.path.exists(cache_path):
        dirty = True
    if dirty:
        print(f"Fetching {endpoint}")
        response = requests.get(endpoint, stream=True)
        response.raise_for_status()
        if not write_cache:
            return response.json()
        print(f"Caching {endpoint}")
        with gzip.open(cache_path, "wb", compresslevel=1) as cache_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                cache_file.write(chunk)
    else:
        print("Reading cache")

    with gzip.open(cache_path, "rt", encoding="utf-8") as cache_file:
        return json.load(cache_file)


def _deserialize_cards(card_jsons: List[JSON]) -> List[ScryCard]:
    cards_data: List[ScryCard]
    if DEBUG == "1":
        print("Process pool disabled")
        cards_data = []
        for card_json in card_jsons:
            try:
                cards_data.append(ScryCard.parse_obj(card_json))
            except Exception:
                print("Failed on: ", repr(card_json))
                raise
    else:
        with ProcessPoolExecutor() as executor:
            cards_futures = executor.map(
                ScryCard.parse_obj, card_jsons, chunksize=DESERIALIZE_BATCH_SIZE
            )
            cards_data = list(cards_futures)
    return cards_data


def scryfetch() -> ScryfallDataSet:
    """Retrieve and deserialize Scryfall object data."""
    cached_bulk_json = None
    if os.path.exists(_cache_path(BULK_DATA_ENDPOINT, ".json.gz")):
        cached_bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=False)
    bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=True, write_cache=False)
    cache_dirty = bulk_json != cached_bulk_json

    bulk_list = ScryObjectList[ScryBulkData].parse_obj(bulk_json)
    sets_list = ScryObjectList[ScrySet].parse_obj(
        _fetch_endpoint(SETS_ENDPOINT, dirty=cache_dirty)
    )
    sets_data = list(sets_list.data)
    while sets_list.has_more:
        sets_list = ScryObjectList[ScrySet].parse_obj(
            _fetch_endpoint(str(sets_list.next_page), dirty=cache_dirty)
        )
        sets_data += sets_list.data

    bulk_data = bulk_list.data
    [cards_endpoint] = [bd.download_uri for bd in bulk_data if bd.type == BULK_TYPE]
    cards_json = cast(List[JSON], _fetch_endpoint(cards_endpoint, dirty=cache_dirty))

    _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=cache_dirty, write_cache=True)

    object_cache_path = _cache_path(OBJECT_CACHE_URL, ".pickle.gz")
    if os.path.exists(object_cache_path):
        if cache_dirty or DEBUG == "1":
            os.remove(object_cache_path)
        else:
            try:
                with gzip.open(object_cache_path, "rb") as object_cache:
                    loaded_data = pickle.load(object_cache)
                if isinstance(loaded_data, ScryfallDataSet):
                    return loaded_data
            except (OSError, pickle.UnpicklingError):
                pass
            print("Error reading object cache, falling back")

    print("Deserializing")
    cards_data = _deserialize_cards(cards_json)

    scryfall_data = ScryfallDataSet(sets=sets_data, cards=cards_data)
    with gzip.open(object_cache_path, "wb", compresslevel=1) as object_cache:
        pickle.dump(scryfall_data, object_cache, protocol=pickle.HIGHEST_PROTOCOL)
    return scryfall_data
