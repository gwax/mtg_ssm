#!/usr/bin/env python3
"""Script to build mtgjson testdata."""
# pylint: disable=protected-access

import copy
from pathlib import Path

from mtg_ssm.scryfall import fetcher, models

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
    "phop": {"Stairs to Infinity", "Tazeem"},
    "phpr": {"Arena"},
    "plc": {"Boom // Bust"},
    "pls": {"Ertai, the Corrupted"},
    "pmbs": {"Hero of Bladehold", "Black Sun's Zenith"},
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
    bulk_json = fetcher._fetch_endpoint(
        fetcher.BULK_DATA_ENDPOINT, dirty=False, write_cache=False
    )
    bulk_data = models.ScryObjectList[models.ScryBulkData].parse_obj(bulk_json).data

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
    accepted_card_ids = {c.id for c in accepted_cards}
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
    for cset in accepted_sets:
        cset.card_count = len([c for c in accepted_cards if c.set == cset.code])

    print("Writing sets")
    sets_list = models.ScryObjectList[models.ScrySet](
        data=accepted_sets,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    sets_list1 = models.ScryObjectList[models.ScrySet](
        data=accepted_sets[: len(accepted_sets) // 2],
        has_more=True,
        next_page=SETS_NEXTPAGE_URL,
        total_cards=None,
        warnings=None,
    )
    sets_list2 = models.ScryObjectList[models.ScrySet](
        data=accepted_sets[len(accepted_sets) // 2 :],
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    TEST_DATA_DIR.mkdir(exist_ok=True)
    with TARGET_SETS_FILE.open("wt", encoding="utf-8") as sets_file:
        sets_file.write(
            sets_list.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        sets_file.write("\n")
    with TARGET_SETS_FILE1.open("wt", encoding="utf-8") as sets_file1:
        sets_file1.write(
            sets_list1.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        sets_file1.write("\n")
    with TARGET_SETS_FILE2.open("wt", encoding="utf-8") as sets_file2:
        sets_file2.write(
            sets_list2.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        sets_file2.write("\n")

    print("Writing migrations")
    accepted_migrations = sorted(
        (m for m in scrydata.migrations if m.new_scryfall_id in accepted_card_ids),
        key=lambda migr: migr.id,
    )
    migrations_list = models.ScryObjectList[models.ScryMigration](
        data=accepted_migrations,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    with TARGET_MIGRATIONS_FILE.open("wt", encoding="utf-8") as migrations_file:
        migrations_file.write(
            migrations_list.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        migrations_file.write("\n")

    print("Writing cards")
    with TARGET_CARDS_FILE.open("wt", encoding="utf-8") as cards_file:
        root_list: models.ScryRootList[models.ScryCard] = models.ScryRootList(
            __root__=accepted_cards
        )
        cards_file.write(
            root_list.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        cards_file.write("\n")

    print("Writing bulk data")
    bulk_list = models.ScryObjectList[models.ScryBulkData](
        data=accepted_bulk,
        has_more=False,
        next_page=None,
        total_cards=None,
        warnings=None,
    )
    with TARGET_BULK_FILE.open("wt", encoding="utf-8") as bulk_file:
        bulk_file.write(
            bulk_list.json(
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
                exclude_none=True,
            )
        )
        bulk_file.write("\n")

    print("Done")


if __name__ == "__main__":
    main()
