"""Legacy record lookup capabilities for older file versions."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from uuid import UUID

from mtg_ssm.containers.indexes import Oracle


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
    "HOP": ["phop"],
    "pMBR": ["pmbs"],
    "pMEI": ["pdrc", "phpr", "pdp11", "pisd", "pdp12", "prtr", "pdp13", "pths"],
    "pPRE": [
        "proe",
        "psom",
        "pmbs",
        "pisd",
        "pdka",
        "pavr",
        "pm13",
        "prtr",
        "pgtc",
        "pdgm",
        "pm14",
        "pths",
    ],
    "pJGP": ["g11"],
    "PO2": ["p02"],
    "pFNM": ["f08"],
    "NMS": ["nem"],
    "pMPR": ["p11"],
    "pLPA": ["pm10", "pwwk", "psom", "pisd"],
    "pWPN": ["pwp10", "pwp11"],
}


def find_scryfall_id(card_row: Dict[str, Any], oracle: Oracle) -> UUID:
    """Heuristically determine the scryfall id for a given input row."""
    set_code = card_row.get("set", "")
    set_codes = [set_code, set_code.lower()] + OTHER_SET_CODE_TO_SET_CODE.get(
        set_code, []
    )
    name = card_row.get("name", "")
    collector_number = card_row.get("number") or None
    mvid = card_row.get("multiverseid") or None
    print(
        f"Searching => Set: {set_code}; Name: {name}; Number: {collector_number}; MVID: {mvid}"
    )
    snnm_keys: List[Tuple[str, str, Optional[str], Optional[int]]] = []
    for set_ in set_codes:
        snnm_keys += [
            (set_, name, collector_number, mvid),
            (set_, name, None, mvid),
            (set_, name, collector_number, None),
            (set_, name, None, None),
        ]
    seen = False
    for snnm_key in snnm_keys:
        found = oracle.index.snnm_to_id.get(snnm_key)
        if found and len(found) == 1:
            [scryfall_id] = found
            found_card = oracle.index.id_to_card[scryfall_id]
            print(
                f"Found ==> Set: {found_card.set}; Name: {found_card.name}; Number: {found_card.collector_number}; MVIDs: {found_card.multiverse_ids}"
            )
            return scryfall_id
        if found:
            seen = True
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
