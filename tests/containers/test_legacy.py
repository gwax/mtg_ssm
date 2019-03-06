"""Tests for mtg_ssm.containers.legacy."""

from typing import Any
from typing import Dict

import pytest

from mtg_ssm.containers import legacy


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
