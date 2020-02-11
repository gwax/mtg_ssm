#!/usr/bin/env python3
"""Script to build mtgjson testdata."""
# pylint: disable=protected-access

import copy
import json
import os
from typing import List
from typing import cast

from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall import models
from mtg_ssm.scryfall import schema

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TARGET_SETS_FILE = os.path.join(TEST_DATA_DIR, "sets.json")
TARGET_SETS_FILE1 = os.path.join(TEST_DATA_DIR, "sets1.json")
TARGET_SETS_FILE2 = os.path.join(TEST_DATA_DIR, "sets2.json")
TARGET_BULK_FILE = os.path.join(TEST_DATA_DIR, "bulk_data.json")
TARGET_CARDS_FILE = os.path.join(TEST_DATA_DIR, "cards.json")

SETS_NEXTPAGE_URL = "https://api.scryfall.com/sets?page=2"

TEST_SETS_TO_CARDS = {
    "arc": {"Leonin Abunas"},
    "bok": {"Faithful Squire // Kaiso, Memory of Loyalty"},
    "chk": {"Bushi Tenderfoot // Kenzo the Hardhearted"},
    "csp": {"Jötun Grunt"},
    "fem": {"Thallid"},
    "hml": {"Cemetery Gate"},
    "hop": {"Akroma's Vengeance", "Dark Ritual"},
    "ice": {"Dark Ritual", "Forest", "Snow-Covered Forest"},
    "isd": {"Abattoir Ghoul", "Delver of Secrets // Insectile Aberration", "Forest"},
    "lea": {"Air Elemental", "Dark Ritual", "Forest"},
    "mma": {"Thallid"},
    "oarc": {"All in Good Time"},
    "ogw": {"Wastes"},
    "ohop": {"Academy at Tolaria West"},
    "opc2": {"Akoum", "Chaotic Aether"},
    "pc2": {"Armored Griffin"},
    "pfrf": {"Dragonscale General"},
    "phop": {"Stairs to Infinity", "Tazeem"},
    "phpr": {"Arena"},
    "plc": {"Boom // Bust"},
    "pls": {"Ertai, the Corrupted"},
    "pmbs": {"Black Sun's Zenith"},
    "ptg": {"Nightmare Moon // Princess Luna"},
    "s00": {"Rhox"},
    "sok": {"Erayo, Soratami Ascendant // Erayo's Essence"},
    "thb": {
        "Wolfwillow Haven",
        "Temple of Plenty",
        "Nyxbloom Ancient",
        "Klothys, God of Destiny",
    },
    "unh": {"Who // What // When // Where // Why"},
    "ust": {"Very Cryptic Command"},
    "vma": {"Academy Elite"},
    "w16": {"Serra Angel"},
}

_OBJECT_SCHEMA = schema.ScryfallUberSchema()


def main() -> None:  # pylint: disable=too-many-locals
    """Read scryfall data and write a subset for use as test data."""
    print("Fetching scryfall data")
    scrydata = fetcher.scryfetch()
    bulk_json = fetcher._fetch_endpoint(
        fetcher.BULK_DATA_ENDPOINT, dirty=False, write_cache=False
    )
    bulk_data = cast(
        List[models.ScryBulkData],
        cast(models.ScryObjectList, fetcher._deserialize_object(bulk_json)).data,
    )

    print("Selecting sets")
    accepted_sets = sorted(
        (s for s in scrydata.sets if s.code in TEST_SETS_TO_CARDS),
        key=lambda sset: sset.code,
    )
    missing_sets = set(TEST_SETS_TO_CARDS.keys()) - {s.code for s in accepted_sets}
    if missing_sets:
        raise Exception("Missing sets: " + str(missing_sets))

    print("Selecting cards")
    accepted_cards = sorted(
        (c for c in scrydata.cards if c.name in TEST_SETS_TO_CARDS.get(c.set, set())),
        key=lambda card: (card.set, card.name, card.collector_number, card.id),
    )
    missing_cards = copy.deepcopy(TEST_SETS_TO_CARDS)
    for card in accepted_cards:
        missing_cards[card.set].discard(card.name)
    missing_cards = {k: v for k, v in missing_cards.items() if v}
    if missing_cards:
        raise Exception("Missing cards: " + str(missing_cards))

    print("Selecting bulk data")
    accepted_bulk = sorted(
        (bd for bd in bulk_data if bd.type == fetcher.BULK_TYPE),
        key=lambda bulk: bulk.type,
    )

    print("Adjusting sets")
    accepted_sets = [
        models.ScrySet(
            id=cset.id,
            code=cset.code,
            mtgo_code=cset.mtgo_code,
            arena_code=cset.arena_code,
            tcgplayer_id=cset.tcgplayer_id,
            name=cset.name,
            set_type=cset.set_type,
            released_at=cset.released_at,
            block_code=cset.block_code,
            block=cset.block,
            parent_set_code=cset.parent_set_code,
            card_count=len([c for c in accepted_cards if c.set == cset.code]),
            digital=cset.digital,
            foil_only=cset.foil_only,
            icon_svg_uri=cset.icon_svg_uri,
            search_uri=cset.search_uri,
            scryfall_uri=cset.scryfall_uri,
            uri=cset.uri,
        )
        for cset in accepted_sets
    ]

    print("Writing sets")
    sets_list = models.ScryObjectList(
        data=accepted_sets,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    sets_list1 = models.ScryObjectList(
        data=accepted_sets[:5],
        has_more=True,
        next_page=models.URI(SETS_NEXTPAGE_URL),
        total_cards=None,
        warnings=None,
    )
    sets_list2 = models.ScryObjectList(
        data=accepted_sets[5:],
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    with open(TARGET_SETS_FILE, "wt", encoding="utf-8") as sets_file:
        json.dump(
            _OBJECT_SCHEMA.dump(sets_list).data,
            sets_file,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        sets_file.write("\n")
    with open(TARGET_SETS_FILE1, "wt", encoding="utf-8") as sets_file1:
        json.dump(
            _OBJECT_SCHEMA.dump(sets_list1).data,
            sets_file1,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        sets_file1.write("\n")
    with open(TARGET_SETS_FILE2, "wt", encoding="utf-8") as sets_file2:
        json.dump(
            _OBJECT_SCHEMA.dump(sets_list2).data,
            sets_file2,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        sets_file2.write("\n")

    print("Writing cards")
    with open(TARGET_CARDS_FILE, "wt", encoding="utf-8") as cards_file:
        json.dump(
            [_OBJECT_SCHEMA.dump(c).data for c in accepted_cards],
            cards_file,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        cards_file.write("\n")

    print("Writing bulk data")
    bulk_list = models.ScryObjectList(
        data=accepted_bulk,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    with open(TARGET_BULK_FILE, "wt", encoding="utf-8") as bulk_file:
        json.dump(
            _OBJECT_SCHEMA.dump(bulk_list).data,
            bulk_file,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        bulk_file.write("\n")

    print("Done")


if __name__ == "__main__":
    main()
