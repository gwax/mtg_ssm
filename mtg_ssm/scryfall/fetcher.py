"""Scryfall data fetcher."""

from concurrent.futures import ProcessPoolExecutor
import gzip
import json
import os
import pickle
import tempfile
from typing import Any
from typing import List
from typing import Mapping
from typing import Union
from typing import cast
import uuid

import appdirs
import requests

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.scryfall import schema
from mtg_ssm.scryfall.models import ScryBulkData
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScryObject
from mtg_ssm.scryfall.models import ScryObjectList
from mtg_ssm.scryfall.models import ScrySet

APP_AUTHOR = "gwax"
APP_NAME = "mtg_ssm"
CACHE_DIR = appdirs.user_cache_dir(APP_NAME, APP_AUTHOR)

BULK_DATA_ENDPOINT = "https://api.scryfall.com/bulk-data"
SETS_ENDPOINT = "https://api.scryfall.com/sets"
BULK_TYPE = "default_cards"
OBJECT_CACHE_URL = "file://$CACHE/pickled_object"

DESERIALIZE_BATCH_SIZE = 50
_OBJECT_SCHEMA = schema.ScryfallUberSchema()

JSON = Union[str, int, float, bool, None, Mapping[str, Any], List[Any]]


def _cache_path(endpoint: str) -> str:
    cache_id = uuid.uuid5(uuid.NAMESPACE_URL, endpoint)
    return os.path.join(CACHE_DIR, str(cache_id))


def _fetch_endpoint(endpoint: str, *, dirty: bool, write_cache: bool = True) -> JSON:
    print(f"Retrieving {endpoint}")
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = _cache_path(endpoint)
    if not os.path.exists(cache_path):
        dirty = True
    if dirty:
        print(f"Fetching {endpoint}")
        response = requests.get(endpoint, stream=True)
        response.raise_for_status()
        if write_cache:
            print(f"Caching {endpoint}")
        else:
            temp_cache = tempfile.NamedTemporaryFile()
            cache_path = temp_cache.name
        with gzip.open(cache_path, "wb") as cache_file:
            for chunk in response.iter_content(chunk_size=1024):
                cache_file.write(chunk)
    else:
        print("Reading cache")

    with gzip.open(cache_path, "rt") as cache_file:
        return json.load(cache_file)


def _deserialize_object(card_json: JSON) -> Union[ScryObject, List[ScryObject]]:
    return _OBJECT_SCHEMA.load(card_json).data


def scryfetch() -> ScryfallDataSet:
    """Retrieve and deserialize Scryfall object data."""
    cached_bulk_json = None
    if os.path.exists(_cache_path(BULK_DATA_ENDPOINT)):
        cached_bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=False)
    bulk_json = _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=True, write_cache=False)
    cache_dirty = bulk_json != cached_bulk_json

    bulk_list: ScryObjectList = cast(ScryObjectList, _deserialize_object(bulk_json))
    sets_list = cast(
        ScryObjectList,
        _deserialize_object(_fetch_endpoint(SETS_ENDPOINT, dirty=cache_dirty)),
    )
    sets_data = cast(List[ScrySet], sets_list.data)
    while sets_list.has_more:
        sets_list = cast(
            ScryObjectList,
            _deserialize_object(
                _fetch_endpoint(str(sets_list.next_page), dirty=cache_dirty)
            ),
        )
        sets_data += cast(List[ScrySet], sets_list.data)

    bulk_data = cast(List[ScryBulkData], bulk_list.data)
    [cards_endpoint] = [bd.permalink_uri for bd in bulk_data if bd.type == BULK_TYPE]
    cards_json = cast(List[JSON], _fetch_endpoint(cards_endpoint, dirty=cache_dirty))

    _fetch_endpoint(BULK_DATA_ENDPOINT, dirty=cache_dirty, write_cache=True)

    if os.path.exists(_cache_path(OBJECT_CACHE_URL)) and not cache_dirty:
        try:
            with gzip.open(_cache_path(OBJECT_CACHE_URL), "rb") as object_cache:
                loaded_data = pickle.load(object_cache)
            if isinstance(loaded_data, ScryfallDataSet):
                return loaded_data
        except (OSError, pickle.UnpicklingError):
            pass
        print("Error reading object cache, falling back")

    print("Deserializing")
    with ProcessPoolExecutor() as executor:
        cards_future = executor.map(
            _deserialize_object, cards_json, chunksize=DESERIALIZE_BATCH_SIZE
        )
        cards_data = cast(List[ScryCard], list(cards_future))

    scryfall_data = ScryfallDataSet(sets=sets_data, cards=cards_data)
    with gzip.open(_cache_path(OBJECT_CACHE_URL), "wb") as object_cache:
        pickle.dump(scryfall_data, object_cache)
    return scryfall_data
