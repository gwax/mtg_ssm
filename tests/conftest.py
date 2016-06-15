"""pytest test configuration file."""

import collections
import json
import os

import pytest

MTGJSON_FILENAME = os.path.join(
    os.path.dirname(__file__), 'data', 'AllSets_testdata.json')


@pytest.fixture(scope='session')
def sets_data():
    """MTGJSON sets data fixture."""
    with open(MTGJSON_FILENAME, 'rt') as mtgjson_datafile:
        return json.load(
            mtgjson_datafile, object_pairs_hook=collections.OrderedDict)


@pytest.fixture(scope='session')
def cards_data(sets_data):
    """MTGJSON cards data fixture."""
    return collections.OrderedDict(
        (card_data['id'], card_data)
        for set_data in sets_data.values()
        for card_data in set_data['cards']
    )
