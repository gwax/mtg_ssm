"""Tests for mtg_ssm.scryfall.models."""

import msgspec

from mtg_ssm.scryfall.models import ScrySet, ScrySetType


def test_scryset_supports_eternal_set_type() -> None:
    payload = b"""{
        "object": "set",
        "id": "f0d89b4b-1f4f-4b22-a201-e1e84b4a5d5f",
        "code": "tmc",
        "name": "Teenage Mutant Ninja Turtles Eternal",
        "set_type": "eternal",
        "card_count": 8,
        "digital": false,
        "foil_only": false,
        "icon_svg_uri": "https://svgs.scryfall.io/sets/default.svg?1694404800",
        "search_uri": "https://api.scryfall.com/cards/search?order=set&q=e%3Atmc&unique=prints",
        "scryfall_uri": "https://scryfall.com/sets/tmc",
        "uri": "https://api.scryfall.com/sets/tmc"
    }"""

    scryset = msgspec.json.decode(payload, type=ScrySet)

    assert scryset.set_type is ScrySetType.ETERNAL
