"""Tests for mtg_ssm.scryfall.models."""

import msgspec

from mtg_ssm.scryfall.models import (
    ScryCard,
    ScryCardLayout,
    ScryFormat,
    ScryLegality,
    ScrySet,
    ScrySetType,
)


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


def test_scrycard_supports_front_card_and_competitive_brawl(cards_data: list[ScryCard]) -> None:
    payload = msgspec.to_builtins(cards_data[0])
    payload["layout"] = "front_card"
    payload["legalities"]["competitivebrawl"] = "not_legal"

    card = msgspec.json.decode(msgspec.json.encode(payload), type=ScryCard)

    assert card.layout is ScryCardLayout.FRONT_CARD
    assert card.legalities[ScryFormat.COMPETITIVEBRAWL] is ScryLegality.NOT_LEGAL


def test_scrycard_supports_null_preview_source_uri(cards_data: list[ScryCard]) -> None:
    payload = msgspec.to_builtins(cards_data[0])
    payload["preview"] = {
        "source": "Scryfall",
        "source_uri": None,
        "previewed_at": "2026-08-27",
    }

    card = msgspec.json.decode(msgspec.json.encode(payload), type=ScryCard)

    assert card.preview is not None
    assert card.preview.source_uri is None
