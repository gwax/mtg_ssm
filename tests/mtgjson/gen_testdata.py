#!/usr/bin/env python3
"""Script to build mtgjson testdata."""

import collections
import json
import os

from mtg_ssm.mtgjson import downloader

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATA_DIR = os.path.join(TEST_DATA_DIR, 'source_data')
TARGET_MTGJSON_FILE = os.path.join(TEST_DATA_DIR, 'AllSets_testdata.json')

INCLUDED = {
    'LEA': {'Air Elemental', 'Dark Ritual', 'Forest'},
    'FEM': {'Thallid'},
    'S00': {'Rhox'},
    'ICE': {'Dark Ritual', 'Forest', 'Snow-Covered Forest'},
    'VMA': {'Academy Elite'},
    'pMGD': {'Black Sun\'s Zenith'},
    'HML': {'Cemetery Gate'},
    'ISD': {
        'Abattoir Ghoul', 'Delver of Secrets', 'Insectile Aberration',
        'Forest'},
    'ARC': {'All in Good Time', 'Leonin Abunas'},
    'HOP': {'Academy at Tolaria West', 'Akroma\'s Vengeance', 'Dark Ritual'},
    'PC2': {'Akoum', 'Armored Griffin', 'Chaotic Æther', 'Stairs to Infinity'},
    'MMA': {'Thallid'},
    'pMEI': {'Arena'},
    'PLS': {'Ertai, the Corrupted'},
}


def main():
    """Filter source mtgjson data and dump testdata."""
    print('Fetching mtgjson data.')
    downloader.fetch_mtgjson(DATA_DIR)
    print('Reading mtgjson data.')
    mtg_data = downloader.read_mtgjson(DATA_DIR)

    print('Generating testdata.')
    testdata = collections.OrderedDict()
    for setcode, setdata in mtg_data.items():
        if setcode not in INCLUDED:
            continue
        testsetdata = collections.OrderedDict(
            (k, v) for k, v in setdata.items() if k != 'cards')
        testsetdata['cards'] = [
            c for c in setdata['cards'] if c['name'] in INCLUDED[setcode]]
        testdata[setcode] = testsetdata

    print('Writing testdata.')
    with open(TARGET_MTGJSON_FILE, 'w') as mtgjson_testfile:
        json.dump(
            testdata, mtgjson_testfile, ensure_ascii=False, indent=2,
            sort_keys=False)
    print('Done')


if __name__ == '__main__':
    main()
