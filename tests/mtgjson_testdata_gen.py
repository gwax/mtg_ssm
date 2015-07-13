"""Script to build mtgjson testdata."""

import collections
import json
import os


SOURCE_MTGJSON_FILE = os.path.join(
    os.path.dirname(__file__), '..', 'data', 'AllSets.json')
TARGET_MTGJSON_FILE = os.path.join(
    os.path.dirname(__file__), 'data', 'AllSets_testdata.json')

INCLUDED = {
    'LEA': {'Air Elemental', 'Forest'},
    'ICE': {'Forest', 'Snow-Covered Forest'},
    'VMA': {'Academy Elite'},
    'pMGD': {'Black Sun\'s Zenith'},
    'HML': {'Cemetery Gate'},
    'ISD': {'Abattoir Ghoul', 'Delver of Secrets', 'Insectile Aberration'},
    'ARC': {'All in Good Time', 'Leonin Abunas'},
    'HOP': {'Academy at Tolaria West', 'Akroma\'s Vengeance'},
    'PC2': {'Akoum', 'Armored Griffin', 'Chaotic Æther', 'Stairs to Infinity'},

}


def main():
    """Filter source mtgjson data and dump testdata."""
    with open(SOURCE_MTGJSON_FILE, 'r') as mtgjson_file:
        mtg_data = json.load(
            mtgjson_file, object_pairs_hook=collections.OrderedDict)

    testdata = collections.OrderedDict()
    for setcode, setdata in mtg_data.items():
        if setcode not in INCLUDED:
            continue
        testsetdata = collections.OrderedDict(
            (k, v) for k, v in setdata.items() if k != 'cards')
        testsetdata['cards'] = [
            c for c in setdata['cards'] if c['name'] in INCLUDED[setcode]]
        testdata[setcode] = testsetdata

    with open(TARGET_MTGJSON_FILE, 'w') as mtgjson_testfile:
        json.dump(
            testdata, mtgjson_testfile, ensure_ascii=False, indent=2,
            sort_keys=False)


if __name__ == '__main__':
    main()
