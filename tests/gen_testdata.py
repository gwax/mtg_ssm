#!/usr/bin/env python3
"""Script to build mtgjson testdata."""
# pylint: disable=protected-access

import copy
from pathlib import Path
from typing import List, cast

import msgspec

from mtg_ssm.scryfall import fetcher, models


class Error(Exception):
    """Base class for exceptions in this module."""


class MissingScryfallDataError(Error):
    """Exception raised for missing Scryfall data."""


TEST_DATA_DIR = Path(__file__).parent / "data"
TARGET_SETS_FILE = TEST_DATA_DIR / "sets.json"
TARGET_SETS_FILE1 = TEST_DATA_DIR / "sets1.json"
TARGET_SETS_FILE2 = TEST_DATA_DIR / "sets2.json"
TARGET_BULK_FILE = TEST_DATA_DIR / "bulk_data.json"
TARGET_CARDS_FILE = TEST_DATA_DIR / "cards.json"
TARGET_MIGRATIONS_FILE = TEST_DATA_DIR / "migrations.json"

SETS_NEXTPAGE_URL = "https://api.scryfall.com/sets?page=2"

TEST_SETS_TO_CARDS = {
    "arc": {"Leonin Abunas"},
    "bok": {"Faithful Squire // Kaiso, Memory of Loyalty"},
    "chk": {"Bushi Tenderfoot // Kenzo the Hardhearted", "Boseiju, Who Shelters All"},
    "csp": {"Jötun Grunt"},
    "fem": {"Thallid"},
    "hml": {"Cemetery Gate"},
    "hop": {"Akroma's Vengeance", "Dark Ritual"},
    "ice": {"Dark Ritual", "Forest", "Snow-Covered Forest"},
    "isd": {"Abattoir Ghoul", "Delver of Secrets // Insectile Aberration", "Forest"},
    "khm": {"Cosmos Elixir", "A-Cosmos Elixir"},
    "lea": {"Air Elemental", "Dark Ritual", "Forest"},
    "mbs": {"Hero of Bladehold", "Black Sun's Zenith"},
    "mma": {"Thallid"},
    "neo": {"Boseiju, Who Endures"},
    "oarc": {"All in Good Time"},
    "ogw": {"Wastes"},
    "ohop": {"Academy at Tolaria West"},
    "opc2": {"Akoum", "Chaotic Aether"},
    "p03": {"Goblin"},
    "pc2": {"Armored Griffin"},
    "pfrf": {"Dragonscale General"},
    "phop": {"Stairs to Infinity"},
    "phpr": {"Arena"},
    "plc": {"Boom // Bust"},
    "pls": {"Ertai, the Corrupted"},
    "pdci": {"Black Sun's Zenith", "Tazeem"},
    "pmbs": {"Hero of Bladehold"},
    "pneo": {"Boseiju, Who Endures"},
    "prna": {"Tithe Taker"},
    "prw2": {"Plains"},
    "ptg": {"Nightmare Moon // Princess Luna"},
    "ren": {"Sylvan Library"},
    "rna": {"Tithe Taker"},
    "s00": {"Rhox"},
    "sld": {"Goblin", "Viscera Seer", "Doubling Cube // Doubling Cube"},
    "sok": {"Erayo, Soratami Ascendant // Erayo's Essence"},
    "sunf": {"Happy Dead Squirrel"},
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


def main() -> None:  # pylint: disable=too-many-locals,too-many-statements
    """Read scryfall data and write a subset for use as test data."""
    print("Fetching scryfall data")
    scrydata = fetcher.scryfetch()
    bulk_data_list = msgspec.json.decode(
        fetcher._fetch_endpoint(fetcher.BULK_DATA_ENDPOINT), type=models.ScryList
    )
    bulk_data = cast(List[models.ScryBulkData], bulk_data_list.data)

    print("Selecting sets")
    accepted_sets = sorted(
        (s for s in scrydata.sets if s.code in TEST_SETS_TO_CARDS),
        key=lambda sset: sset.code,
    )
    missing_sets = set(TEST_SETS_TO_CARDS.keys()) - {s.code for s in accepted_sets}
    if missing_sets:
        raise MissingScryfallDataError("Missing sets: " + str(missing_sets))

    print("Selecting cards")
    accepted_cards = sorted(
        (c for c in scrydata.cards if c.name in TEST_SETS_TO_CARDS.get(c.set, set())),
        key=lambda card: (card.set, card.name, card.collector_number, card.id),
    )
    accepted_card_ids = {c.id for c in accepted_cards}
    missing_cards = copy.deepcopy(TEST_SETS_TO_CARDS)
    for card in accepted_cards:
        missing_cards[card.set].discard(card.name)
    missing_cards = {k: v for k, v in missing_cards.items() if v}
    if missing_cards:
        raise MissingScryfallDataError("Missing cards: " + str(missing_cards))

    print("Selecting bulk data")
    accepted_bulk = sorted(
        (bd for bd in bulk_data if bd.type == fetcher.BULK_TYPE),
        key=lambda bulk: bulk.type,
    )

    print("Adjusting sets")
    for cset in accepted_sets:
        cset.card_count = len([c for c in accepted_cards if c.set == cset.code])

    print("Writing sets")
    sets_list = models.ScryList(
        data=accepted_sets,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    sets_list1 = models.ScryList(
        data=accepted_sets[: len(accepted_sets) // 2],
        has_more=True,
        next_page=SETS_NEXTPAGE_URL,
        total_cards=None,
        warnings=None,
    )
    sets_list2 = models.ScryList(
        data=accepted_sets[len(accepted_sets) // 2 :],
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    TEST_DATA_DIR.mkdir(exist_ok=True)
    with TARGET_SETS_FILE.open("wb") as sets_file:
        sets_file.write(msgspec.json.format(msgspec.json.encode(sets_list), indent=2))
        sets_file.write(b"\n")
    with TARGET_SETS_FILE1.open("wb") as sets_file1:
        sets_file1.write(msgspec.json.format(msgspec.json.encode(sets_list1), indent=2))
        sets_file1.write(b"\n")
    with TARGET_SETS_FILE2.open("wb") as sets_file2:
        sets_file2.write(msgspec.json.format(msgspec.json.encode(sets_list2), indent=2))
        sets_file2.write(b"\n")

    print("Writing migrations")
    accepted_migrations = sorted(
        (m for m in scrydata.migrations if m.new_scryfall_id in accepted_card_ids),
        key=lambda migr: migr.id,
    )
    migrations_list = models.ScryList(
        data=accepted_migrations,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    with TARGET_MIGRATIONS_FILE.open("wb") as migrations_file:
        migrations_file.write(
            msgspec.json.format(msgspec.json.encode(migrations_list), indent=2)
        )
        migrations_file.write(b"\n")

    print("Writing cards")
    with TARGET_CARDS_FILE.open("wb") as cards_file:
        cards_file.write(
            msgspec.json.format(msgspec.json.encode(accepted_cards), indent=2)
        )
        cards_file.write(b"\n")

    print("Writing bulk data")
    bulk_list = models.ScryList(
        data=accepted_bulk,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    with TARGET_BULK_FILE.open("wb") as bulk_file:
        bulk_file.write(msgspec.json.format(msgspec.json.encode(bulk_list), indent=2))
        bulk_file.write(b"\n")

    print("Done")


if __name__ == "__main__":
    main()
