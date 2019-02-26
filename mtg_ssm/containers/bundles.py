"""Data bundle definitions."""

from typing import List
from typing import NamedTuple

from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.scryfall.models import ScrySet


class ScryfallDataSet(NamedTuple):
    """Bundle for storing Scryfall data."""

    sets: List[ScrySet]
    cards: List[ScryCard]
