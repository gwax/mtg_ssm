"""Container for all data related to a collection."""

from dataclasses import dataclass

from mtg_ssm.containers import counts
from mtg_ssm.containers.counts import ScryfallCardCount
from mtg_ssm.containers.indexes import Oracle


@dataclass
class MagicCollection:
    """Collection object for tracking magic cards and counts."""

    oracle: Oracle
    counts: ScryfallCardCount

    def __add__(self, other: "MagicCollection") -> "MagicCollection":
        if not isinstance(other, MagicCollection):
            return NotImplemented
        return MagicCollection(
            oracle=self.oracle,
            counts=counts.merge_card_counts(self.counts, other.counts),
        )

    def __iadd__(self, other: "MagicCollection") -> "MagicCollection":
        if not isinstance(other, MagicCollection):
            return NotImplemented
        self.counts = counts.merge_card_counts(self.counts, other.counts)
        return self

    def __sub__(self, other: "MagicCollection") -> "MagicCollection":
        if not isinstance(other, MagicCollection):
            return NotImplemented
        return MagicCollection(
            oracle=self.oracle,
            counts=counts.diff_card_counts(self.counts, other.counts),
        )

    def __isub__(self, other: "MagicCollection") -> "MagicCollection":
        if not isinstance(other, MagicCollection):
            return NotImplemented
        self.counts = counts.diff_card_counts(self.counts, other.counts)
        return self
