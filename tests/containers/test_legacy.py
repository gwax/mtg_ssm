"""Tests for mtg_ssm.containers.legacy."""
# pylint: disable=redefined-outer-name

from typing import Any, Dict
from uuid import UUID

import pytest

from mtg_ssm.containers import legacy
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.indexes import Oracle


@pytest.fixture(scope="session")
def oracle(scryfall_data: ScryfallDataSet) -> Oracle:
    """Oracle fixture."""
    return Oracle(scryfall_data)


@pytest.mark.parametrize(
    "card_row, expected",
    [
        pytest.param({}, {}),
        pytest.param({"gar": "bage"}, {}),
        pytest.param({"nonfoil": "1", "foil": "3"}, {"nonfoil": 1, "foil": 3}),
        pytest.param({"nonfoil": "0", "foil": "0"}, {}),
        pytest.param({"copies": "1", "foils": "3"}, {"nonfoil": 1, "foil": 3}),
        pytest.param(
            {"copies": "1", "nonfoil": "3", "foils": "5", "foil": "7"},
            {"nonfoil": 4, "foil": 12},
        ),
    ],
)
def test_extract_counts(card_row: Dict[str, Any], expected: Dict[str, int]) -> None:
    assert legacy.extract_counts(card_row) == expected


@pytest.mark.parametrize(
    "card_row, expected",
    [
        pytest.param(
            {},
            None,
            marks=pytest.mark.xfail(raises=legacy.NoMatchError),
            id="not found",
        ),
        pytest.param(
            {"set": "FEM", "name": "Thallid", "number": "74a"},
            UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233"),
            id="snn__",
        ),
        pytest.param(
            {"set": "FEM", "name": "Thallid", "multiverseid": 1924},
            UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233"),
            id="sn_m_",
        ),
        pytest.param(
            {"set": "FEM", "name": "Thallid", "artist": "Edward P. Beard, Jr."},
            UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233"),
            id="sn__a",
        ),
        pytest.param(
            {"set": "MMA", "name": "Thallid"},
            UUID("69d20d28-76e9-4e6e-95c3-f88c51dfabfd"),
            id="sn___",
        ),
        pytest.param(
            {"name": "Thallid", "artist": "Trevor Claxton"},
            UUID("69d20d28-76e9-4e6e-95c3-f88c51dfabfd"),
            id="_n__a",
        ),
        pytest.param(
            {"set": "FEM", "name": "Thallid"},
            None,
            marks=pytest.mark.xfail(raises=legacy.MultipleMatchError),
            id="sn__ multiple",
        ),
        pytest.param(
            {"set": "pMBR", "name": "Black Sun's Zenith", "artist": "James Paick"},
            UUID("dd88131a-2811-4a1f-bb9a-c82e12c1493b"),
            id="set remap",
        ),
        pytest.param(
            {"name": "Dragonscale General", "artist": "William Murai"},
            UUID("6daabdc2-e8a8-41a6-a9f0-1973d9c31d39"),
            id="artist remap",
        ),
    ],
)
def test_find_scryfall_id(
    card_row: Dict[str, Any], expected: UUID, oracle: Oracle
) -> None:
    assert legacy.find_scryfall_id(card_row, oracle) == expected


@pytest.mark.parametrize(
    "card_row, expected",
    [
        pytest.param({}, {}),
        pytest.param({"set": "MMA", "name": "Thallid"}, {}),
        pytest.param(
            {"set": "MMA", "name": "Thallid", "copies": "1"},
            {"scryfall_id": UUID("69d20d28-76e9-4e6e-95c3-f88c51dfabfd"), "nonfoil": 1},
        ),
    ],
)
def test_coerce_row(
    card_row: Dict[str, Any], expected: Dict[str, Any], oracle: Oracle
) -> None:
    assert legacy.coerce_row(card_row, oracle) == expected
