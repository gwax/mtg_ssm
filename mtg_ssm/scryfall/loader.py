"""Download, validate, and parse Scryfall data."""

from enum import Enum
import os
import time
import contextvars
from mtg_ssm.scryfall import models, schema
from typing import List, NamedTuple
import requests
import json

class ScryfallData(NamedTuple):
    """Response payload for Scryfall data loader."""

    sets: List[models.ScryfallSet]
    cards: List[models.ScryfallCard]


def fetch(data_path) -> ScryfallData:
    """Fetch all scryfall data from web or cache."""
    valid_cache = True

    if not os.path.exists(data_path):
        os.makedirs(data_path)
        valid_cache = False
    elif not os.path.isdir(data_path):
        raise Exception(f'data_path: {data_path} must be a folder')

    session = requests.Session()
    list_schema = schema.ScryfallListSchema()
    card_schema = schema.ScryfallCardSchema()

    bulk_data_path = os.path.join(data_path, 'bulk_data.json')
    sets_data_path = os.path.join(data_path, 'sets.json')
    cards_data_path = os.path.join(data_path, 'cards.json')

    print('Fetching bulk data information')
    bulk_data_response = session.get('https://api.scryfall.com/bulk-data')
    bulk_data_response.raise_for_status()
    bulk_json = bulk_data_response.json()
    bulk_data = list_schema.load(bulk_json).data
    assert not bulk_data.has_more
    if os.path.exists(bulk_data_path):
        with open(bulk_data_path, 'rt') as bdf:
            old_bulk_data = list_schema.load(json.load(bdf)).data
        if bulk_data != old_bulk_data:
            valid_cache = False
    else:
        valid_cache = False

    if valid_cache:
        with open(sets_data_path, 'rt') as sdf:
            sets_json = json.load(sdf)
        with open(cards_data_path, 'rt') as cdf:
            cards_json = json.load(cdf)
    else:
        print('Fetching sets information')
        sets_response = session.get('https://api.scryfall.com/sets')
        sets_response.raise_for_status()
        sets_json = sets_response.json()

        print('Fetching cards information')
        cards_response = session.get('https://archive.scryfall.com/json/scryfall-default-cards.json')
        cards_response.raise_for_status()
        cards_json = cards_response.json()

    if not valid_cache:
        with open(cards_data_path, 'wt') as cdf:
            json.dump(cards_json, cdf)
        with open(sets_data_path, 'wt') as sdf:
            json.dump(sets_json, sdf)
        with open(bulk_data_path, 'wt') as bdf:
            json.dump(bulk_json, bdf)

    print('Reading sets information')
    sets_list_data = list_schema.load(sets_json).data
    assert not sets_list_data.has_more
    print('Reading cards information')
    cards_data = [card_schema.load(card).data for card in cards_json]

    return ScryfallData(sets=sets_list_data.data, cards=cards_data)
