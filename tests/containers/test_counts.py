"""Tests for mtg_ssm.mtg.counts"""
# pylint: disable=redefined-outer-name

from typing import Any, Dict, List
from uuid import UUID

import pytest

from mtg_ssm.containers import counts
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.counts import CardNotFoundError, CountType, ScryfallCardCount
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.containers.legacy import NoMatchError


@pytest.fixture(scope="session")
def oracle(scryfall_data: ScryfallDataSet) -> Oracle:
    """Oracle fixture."""
    return Oracle(scryfall_data)


@pytest.mark.parametrize(
    "in_card_counts, out_card_count",
    [
        pytest.param([], {}, id="no inputs"),
        pytest.param(
            [{UUID(int=1): {CountType.NONFOIL: 2}}],
            {UUID(int=1): {CountType.NONFOIL: 2}},
            id="single input",
        ),
        pytest.param(
            [
                {UUID(int=1): {CountType.NONFOIL: 2}},
                {UUID(int=1): {CountType.NONFOIL: 1, CountType.FOIL: 4}},
            ],
            {UUID(int=1): {CountType.NONFOIL: 3, CountType.FOIL: 4}},
            id="mixed types",
        ),
        pytest.param(
            [
                {UUID(int=1): {CountType.NONFOIL: 2}},
                {UUID(int=1): {CountType.FOIL: 1}, UUID(int=2): {CountType.NONFOIL: 3}},
                {UUID(int=1): {CountType.FOIL: 5}},
            ],
            {
                UUID(int=1): {CountType.NONFOIL: 2, CountType.FOIL: 6},
                UUID(int=2): {CountType.NONFOIL: 3},
            },
            id="multiple inputs",
        ),
    ],
)
def test_merge_card_counts(
    in_card_counts: List[ScryfallCardCount], out_card_count: ScryfallCardCount
) -> None:
    assert counts.merge_card_counts(*in_card_counts) == out_card_count


@pytest.mark.parametrize(
    "left, right, output",
    [
        pytest.param({}, {}, {}, id="no inputs"),
        pytest.param(
            {UUID(int=1): {CountType.NONFOIL: 2}},
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {UUID(int=1): {CountType.NONFOIL: 1}},
            id="positive output",
        ),
        pytest.param(
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {UUID(int=1): {CountType.NONFOIL: 2}},
            {UUID(int=1): {CountType.NONFOIL: -1}},
            id="negative output",
        ),
        pytest.param(
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {},
            id="negated",
        ),
        pytest.param(
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {UUID(int=2): {CountType.NONFOIL: 1}},
            {UUID(int=1): {CountType.NONFOIL: 1}, UUID(int=2): {CountType.NONFOIL: -1}},
            id="mixed cards",
        ),
        pytest.param(
            {UUID(int=1): {CountType.NONFOIL: 1}},
            {UUID(int=1): {CountType.FOIL: 1}},
            {UUID(int=1): {CountType.NONFOIL: 1, CountType.FOIL: -1}},
            id="mixed count types",
        ),
    ],
)
def test_diff_card_counts(
    left: ScryfallCardCount, right: ScryfallCardCount, output: ScryfallCardCount
) -> None:
    assert counts.diff_card_counts(left, right) == output


@pytest.mark.parametrize(
    "card_rows, output",
    [
        pytest.param([], {}, id="nothing"),
        pytest.param([{}], {}, id="empty"),
        pytest.param([{"foo": "bar"}], {}, id="no count"),
        pytest.param(
            [{"foo": "bar", "foil": "1"}],
            {},
            marks=pytest.mark.xfail(raises=NoMatchError),
            id="no id",
        ),
        pytest.param(
            [{"scryfall_id": UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"), "foil": 1}],
            {UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"): {counts.CountType.FOIL: 1}},
            id="id and int",
        ),
        pytest.param(
            [{"scryfall_id": "9d26f171-5bb6-463c-8473-53b6cc27ed66", "foil": "1"}],
            {UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"): {counts.CountType.FOIL: 1}},
            id="text and text",
        ),
        pytest.param(
            [{"scryfall_id": "00000000-0000-0000-0000-000000000001", "nonfoil": "1"}],
            {},
            marks=pytest.mark.xfail(raises=CardNotFoundError),
            id="count with bad id",
        ),
        pytest.param(
            [{"scryfall_id": "00000000-0000-0000-0000-000000000001", "nonfoil": ""}],
            {},
            id="no count with bad id",
        ),
        pytest.param(
            [
                {
                    "scryfall_id": "9d26f171-5bb6-463c-8473-53b6cc27ed66",
                    "foil": "1",
                    "nonfoil": "",
                }
            ],
            {UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"): {counts.CountType.FOIL: 1}},
            id="empty string",
        ),
        pytest.param(
            [
                {"scryfall_id": "9d26f171-5bb6-463c-8473-53b6cc27ed66", "foil": "1"},
                {"scryfall_id": "758abd53-6ad2-406e-8615-8e48678405b4", "foil": "0"},
                {"scryfall_id": "0180d9a8-992c-4d55-8ac4-33a587786993", "nonfoil": "1"},
            ],
            {
                UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"): {
                    counts.CountType.FOIL: 1
                },
                UUID("0180d9a8-992c-4d55-8ac4-33a587786993"): {
                    counts.CountType.NONFOIL: 1
                },
            },
            id="multiple",
        ),
        pytest.param(
            [
                {
                    "scryfall_id": UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"),
                    "foil": 1,
                },
                {
                    "scryfall_id": UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"),
                    "nonfoil": 1,
                },
                {
                    "scryfall_id": UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"),
                    "foil": 1,
                },
            ],
            {
                UUID("9d26f171-5bb6-463c-8473-53b6cc27ed66"): {
                    counts.CountType.FOIL: 2,
                    counts.CountType.NONFOIL: 1,
                }
            },
            id="duplicates",
        ),
        pytest.param(
            [
                {
                    "scryfall_id": UUID("585fa2cc-4f77-47ab-8d2c-c68258ced283"),
                    "foil": 1,
                },
            ],
            {
                UUID("9052f5c7-ee3b-457d-97ca-ac6b4518997c"): {
                    counts.CountType.FOIL: 1,
                }
            },
            id="migration",
        ),
    ],
)
def test_aggregate_card_counts(
    oracle: Oracle, card_rows: List[Dict[str, Any]], output: counts.ScryfallCardCount
) -> None:
    assert counts.aggregate_card_counts(card_rows, oracle) == output
