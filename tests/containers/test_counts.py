"""Tests for mtg_ssm.mtg.counts"""

from typing import List
from uuid import UUID

import pytest

from mtg_ssm.containers import counts
from mtg_ssm.containers.counts import CountType
from mtg_ssm.containers.counts import ScryfallCardCount


@pytest.mark.parametrize(
    "in_card_counts, out_card_count",
    [
        pytest.param([], {}, id="no inputs"),
        pytest.param(
            [{UUID(int=1): {CountType.nonfoil: 2}}],
            {UUID(int=1): {CountType.nonfoil: 2}},
            id="single input",
        ),
        pytest.param(
            [
                {UUID(int=1): {CountType.nonfoil: 2}},
                {UUID(int=1): {CountType.nonfoil: 1, CountType.foil: 4}},
            ],
            {UUID(int=1): {CountType.nonfoil: 3, CountType.foil: 4}},
            id="mixed types",
        ),
        pytest.param(
            [
                {UUID(int=1): {CountType.nonfoil: 2}},
                {UUID(int=1): {CountType.foil: 1}, UUID(int=2): {CountType.nonfoil: 3}},
                {UUID(int=1): {CountType.foil: 5}},
            ],
            {
                UUID(int=1): {CountType.nonfoil: 2, CountType.foil: 6},
                UUID(int=2): {CountType.nonfoil: 3},
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
            {UUID(int=1): {CountType.nonfoil: 2}},
            {UUID(int=1): {CountType.nonfoil: 1}},
            {UUID(int=1): {CountType.nonfoil: 1}},
            id="positive output",
        ),
        pytest.param(
            {UUID(int=1): {CountType.nonfoil: 1}},
            {UUID(int=1): {CountType.nonfoil: 2}},
            {UUID(int=1): {CountType.nonfoil: -1}},
            id="negative output",
        ),
        pytest.param(
            {UUID(int=1): {CountType.nonfoil: 1}},
            {UUID(int=1): {CountType.nonfoil: 1}},
            {},
            id="negated",
        ),
        pytest.param(
            {UUID(int=1): {CountType.nonfoil: 1}},
            {UUID(int=2): {CountType.nonfoil: 1}},
            {UUID(int=1): {CountType.nonfoil: 1}, UUID(int=2): {CountType.nonfoil: -1}},
            id="mixed cards",
        ),
        pytest.param(
            {UUID(int=1): {CountType.nonfoil: 1}},
            {UUID(int=1): {CountType.foil: 1}},
            {UUID(int=1): {CountType.nonfoil: 1, CountType.foil: -1}},
            id="mixed count types",
        ),
    ],
)
def test_diff_card_counts(
    left: ScryfallCardCount, right: ScryfallCardCount, output: ScryfallCardCount
) -> None:
    assert counts.diff_card_counts(left, right) == output
