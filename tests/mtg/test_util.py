"""Tests for mtg_ssm.mtg.util."""

from typing import Dict, Optional
from uuid import UUID

import pytest

from mtg_ssm.mtg import util
from mtg_ssm.scryfall.models import ScryCard


@pytest.mark.parametrize(
    "name, expected",
    [
        pytest.param("Forest", True),
        pytest.param("Snow-Covered Forest", False),
        pytest.param("Wastes", False),
        pytest.param("Abattoir Ghoul", False),
    ],
)
def test_is_strict_basic(name: str, expected: bool) -> None:
    assert util.is_strict_basic(name) is expected


@pytest.mark.parametrize(
    "name, card_id, number, variant",
    [
        pytest.param("Thallid", UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233"), 74, "a"),
        pytest.param(
            "Dark Ritual", UUID("ebb6664d-23ca-456e-9916-afcd6f26aa7f"), 98, None
        ),
        pytest.param(
            "Stairs to Infinity", UUID("57f25ead-b3ec-4c40-972d-d750ed2f5319"), 1, "P"
        ),
        pytest.param(
            "Ertai, the Corrupted",
            UUID("66b950d9-8fef-4deb-b51b-26edb90abc56"),
            107,
            None,
        ),
        pytest.param(
            "Ertai, the Corrupted",
            UUID("fbbfeb32-1654-4bf6-9a38-891f1a03e02b"),
            107,
            "★",
        ),
        pytest.param(
            "Viscera Seer",
            UUID("dba1cf83-e13d-401e-b76f-b12a51b307f9"),
            None,
            "VS",
        ),
    ],
)
def test_collector_int_var(
    id_to_card: Dict[UUID, ScryCard],
    name: str,
    card_id: UUID,
    number: Optional[int],
    variant: Optional[str],
) -> None:
    card = id_to_card[card_id]
    assert card.name == name
    assert (number, variant) == util.collector_int_var(card)
