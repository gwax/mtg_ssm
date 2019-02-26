"""Tests for mtg_ssm.containers.indexes."""

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.indexes import ScryfallDataIndex


def test_load_data(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)
