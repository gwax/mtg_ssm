"""Legacy record lookup capabilities for older file versions."""

from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.mtg import util


class Error(Exception):
    """Base exception for this module."""


class NoMatchError(Error):
    """Raised when a matchor(Error):ing card cannot be found."""


class MultipleMatchError(Error):
    """Raised when multiple matching cards are found."""


COUNT_TYPE_TO_OLD_COUNT_TYPES: Dict[str, Set[str]] = {
    "nonfoil": {"nonfoil", "copies"},
    "foil": {"foil", "foils"},
}


def extract_counts(card_row: Dict[str, Any]) -> Dict[str, int]:
    """Convert old count type names to new count type names."""
    renamed_counts = {
        k: sum(int(card_row.get(t) or 0) for t in v)
        for k, v in COUNT_TYPE_TO_OLD_COUNT_TYPES.items()
    }
    return {k: v for k, v in renamed_counts.items() if v}


OTHER_SET_CODE_TO_SET_CODE = {
    # TODO: MOAR!
    "pMEI": ["phpr", "pdrc", "pbok", "pdtp", "pres", "purl", "pdp10", "pfrf", "pori"],
    "pPRE": ["psom", "pdgm", "pths", "pm15", "pktk", "pfrf", "pdtk", "pori", "pbfz"],
    "pJGP": [
        "jgp",
        "g99",
        "g00",
        "g01",
        "g02",
        "g03",
        "g04",
        "g05",
        "g06",
        "g07",
        "g08",
        "g09",
        "g11",
    ],
    "PO2": ["p02"],
    "pFNM": [
        "fnm",
        "f01",
        "f02",
        "f03",
        "f04",
        "f05",
        "f06",
        "f07",
        "f08",
        "f09",
        "f10",
        "f11",
        "f12",
        "f13",
        "f14",
        "f15",
        "f16",
        "f17",
        "f18",
    ],
    "NMS": ["nem"],
    "pARL": ["pal99", "pal00", "pal01", "pal02", "pal03", "pal04", "pal05", "pal06"],
    "VAN": ["pvan"],
    "pGTW": ["pg07", "pg08"],
    "pMGD": ["p10e", "pnph", "pori"],
    "pLPA": ["pmbs", "pavr", "pktk"],
    "pWPN": ["pwwk", "pwp10", "proe"],
    "HOP": ["ohop", "phop"],
    "PC2": ["opc2", "phop"],
    "pWCQ": ["ppro"],
    "DD3_JVC": ["jvc"],
    "DD3_GVL": ["gvl"],
    "DD3_EVG": ["evg"],
    "DD3_DVD": ["dvd"],
    "FRF_UGIN": ["ugin"],
    "PCA": ["opca"],
}

PSUDONYM_TO_ARTIST: Dict[Optional[str], str] = {
    "William Murai": "Willian Murai",
    "Dave Seeley": "David Seeley",
}


def find_scryfall_id(card_row: Dict[str, str], oracle: Oracle) -> UUID:
    """Heuristically determine the scryfall id for a given input row."""
    set_code = card_row.get("set", "")
    set_codes = [set_code, set_code.lower()] + OTHER_SET_CODE_TO_SET_CODE.get(
        set_code, []
    )
    name = card_row.get("name", "")
    collector_number = card_row.get("number") or None
    mvid = int(card_row.get("multiverseid") or -1)
    artist = card_row.get("artist") or None
    artist = PSUDONYM_TO_ARTIST.get(artist, artist)
    print(
        f"Searching => Set: {set_code}; Name: {name}; Number: {collector_number}; MVID: {mvid}"
    )
    snnma_keys: List[
        Tuple[Optional[str], str, Optional[str], Optional[int], Optional[str]]
    ] = []
    for set_ in set_codes:
        snnma_keys += [
            (set_, name, collector_number, None, None),
            (set_, name, None, mvid, None),
            (set_, name, None, None, artist),
            (set_, name, None, None, None),
            (None, name, None, None, artist),
        ]
    seen = False
    for snnma_key in snnma_keys:
        found = oracle.index.snnma_to_id.get(snnma_key)
        if found:
            seen = True
            scryfall_id = None
            if len(found) == 1:
                [scryfall_id] = found
            if util.is_strict_basic(name):
                scryfall_id = sorted(found)[0]
            if scryfall_id is not None:
                found_card = oracle.index.id_to_card[scryfall_id]
                print(
                    f"Found ==> Set: {found_card.set}; Name: {found_card.name}; Number: {found_card.collector_number}; MVIDs: {found_card.multiverse_ids}"
                )
                return scryfall_id
    if seen:
        raise MultipleMatchError(f"Could not find scryfall card for row: {card_row}")
    raise NoMatchError(f"Could not find scryfall card for row: {card_row}")


def coerce_row(card_row: Dict[str, Any], oracle: Oracle) -> Dict[str, Any]:
    """Coerce an unknown older row into a current row.

    If this cannot be done precisely, a warning will be displayed.
    """
    coerced_counts = extract_counts(card_row)
    if not coerced_counts:
        return {}
    coerced_scryfall_id = find_scryfall_id(card_row, oracle)
    return {"scryfall_id": coerced_scryfall_id, **coerced_counts}
