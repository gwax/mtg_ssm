#!/usr/bin/env python3
"""Script to build mtgjson testdata."""

import collections
import json
import os

from mtg_ssm import mtgjson

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_DIR = os.path.join(TEST_DATA_DIR, "source_data")
TARGET_MTGJSON_FILE = os.path.join(TEST_DATA_DIR, "AllSets_testdata.json")

TEST_SETS_TO_CARDS = {
    "LEA": {"Air Elemental", "Dark Ritual", "Forest"},
    "FEM": {"Thallid"},
    "S00": {"Rhox"},
    "ICE": {"Dark Ritual", "Forest", "Snow-Covered Forest"},
    "CSP": {"Jötun Grunt"},
    "VMA": {"Academy Elite"},
    "pMGD": {"Black Sun's Zenith"},
    "HML": {"Cemetery Gate"},
    "ISD": {"Abattoir Ghoul", "Delver of Secrets", "Insectile Aberration", "Forest"},
    "ARC": {"All in Good Time", "Leonin Abunas"},
    "HOP": {"Academy at Tolaria West", "Akroma's Vengeance", "Dark Ritual"},
    "PC2": {"Akoum", "Armored Griffin", "Chaotic Aether", "Stairs to Infinity"},
    "MMA": {"Thallid"},
    "pMEI": {"Arena"},
    "PLS": {"Ertai, the Corrupted"},
    "PLC": {"Boom", "Bust"},
    "OGW": {"Wastes"},
    "BOK": {"Faithful Squire", "Kaiso, Memory of Loyalty"},
    "SOK": {"Erayo, Soratami Ascendant", "Erayo's Essence"},
    "CHK": {"Bushi Tenderfoot", "Kenzo the Hardhearted"},
    "W16": {"Serra Angel"},
}


def main():
    """Filter source mtgjson data and dump testdata."""
    print("Fetching mtgjson data.")
    mtgjson.fetch_mtgjson(DATA_DIR)
    print("Reading mtgjson data.")
    mtg_data = mtgjson.read_mtgjson(DATA_DIR)

    print("Generating testdata.")
    testdata = collections.OrderedDict()
    for setcode, setdata in mtg_data.items():
        if setcode not in TEST_SETS_TO_CARDS:
            continue
        testsetdata = collections.OrderedDict(
            (k, v) for k, v in setdata.items() if k != "cards"
        )
        testsetdata["cards"] = [
            c for c in setdata["cards"] if c["name"] in TEST_SETS_TO_CARDS[setcode]
        ]
        testdata[setcode] = testsetdata

    print("Writing testdata.")
    with open(TARGET_MTGJSON_FILE, "w") as mtgjson_testfile:
        json.dump(
            testdata, mtgjson_testfile, ensure_ascii=False, indent=2, sort_keys=True
        )
    print("Done")


if __name__ == "__main__":
    main()
