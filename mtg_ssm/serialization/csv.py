"""CSV serializer."""

import csv
import datetime as dt
from pathlib import Path
from typing import Any, ClassVar, Dict, Iterable, Mapping

from mtg_ssm.containers import counts
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.counts import CountType
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.scryfall.models import ScryCard
from mtg_ssm.serialization import interface

CSV_HEADER = ["set", "name", "collector_number", "scryfall_id"] + [
    ct.value for ct in CountType
]


def row_for_card(card: ScryCard, card_count: Mapping[CountType, int]) -> Dict[str, Any]:
    """Given a CardPrinting and counts, return a csv row."""
    return {
        "set": card.set.upper(),
        "name": card.name,
        "collector_number": card.collector_number,
        "scryfall_id": card.id,
        **{ct.value: cnt for ct, cnt in card_count.items() if cnt},
    }


def rows_for_cards(
    collection: MagicCollection, verbose: bool
) -> Iterable[Dict[str, Any]]:
    """Generator that yields csv rows from a collection."""
    for card_set in sorted(
        collection.oracle.index.setcode_to_set.values(),
        key=lambda cset: (cset.released_at or dt.date.min, cset.code),
    ):
        for card in collection.oracle.index.setcode_to_cards[card_set.code]:
            card_count = collection.counts.get(card.id, {})
            if verbose or any(card_count.values()):
                yield row_for_card(card, card_count)


class CsvFullDialect(interface.SerializationDialect):
    """csv collection writing a row for every printing"""

    extension: ClassVar[str] = "csv"
    dialect: ClassVar[str] = "csv"

    verbose: ClassVar[bool] = True

    def write(self, path: Path, collection: MagicCollection) -> None:
        """Write collection to a file."""
        with path.open("wt", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, CSV_HEADER)
            writer.writeheader()
            for row in rows_for_cards(collection, self.verbose):
                writer.writerow(row)

    def read(self, path: Path, oracle: Oracle) -> MagicCollection:
        """Read collection from file."""
        with path.open("rt", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            card_counts = counts.aggregate_card_counts(reader, oracle)
        return MagicCollection(oracle=oracle, counts=card_counts)


class CsvTerseDialect(CsvFullDialect):
    """csv collection writing only rows that have counts"""

    dialect: ClassVar[str] = "terse"

    verbose: ClassVar[bool] = False
