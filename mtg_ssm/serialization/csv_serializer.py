"""CSV serializer."""

import csv

from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface

CSV_HEADER = [
    'set',
    'name',
    'name',
    'number',
    'multiverseid',
    'mtgjson_id',
] + [ct.name for ct in models.CountTypes]


def row_from_printing(printing):
    """Given a CardPrinting, return a csv row."""
    csv_row = {
        'set': printing.set_code,
        'name': printing.card_name,
        'number': printing.set_number,
        'multiverseid': printing.multiverseid,
        'mtgjson_id': printing.id_,
    }
    for counttype, count in printing.counts.items():
        if count:
            csv_row[counttype.name] = count
    return csv_row


def csv_rows_from_collection(collection):
    """Generator that yields csv rows from a collection."""
    card_sets = collection.code_to_card_set.values()
    card_sets.sort(key=lambda cset: cset.release_date)
    for card_set in card_sets:
        for printing in card_set.printings:
            yield row_from_printing(printing)


def load_counts_from_row(collection, row):
    """Given a csv DictReader row, read card counts according to mtgjson_id."""
    printing_id = row.get('mtgjson_id')
    printing = collection.id_to_printing.get(printing_id)
    if printing is None:
        raise interface.DeserializationError(
            'Could not match mtgjson_id to known printing for row: %r' % row)

    for counttype in models.CountTypes:
        countname = counttype.name
        count = row.get(countname)
        if count is not None:
            existing = printing.counts.get(counttype, 0)
            printing.counts[counttype] = existing + count


class MtgCsvSerializer(interface.MtgSsmSerializer):
    """MtgSsmSerializer for reading and writing csv files."""

    extensions = {'csv'}

    def write_to_file(self, filename: str) -> None:
        """Write the collection to a csv file."""
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, CSV_HEADER)
            writer.writeheader()
            for row in csv_rows_from_collection(self.collection):
                writer.writerow(row)

    def read_from_file(self, filename: str) -> None:
        """Read collection counts from a csv file."""
        with open(filename, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                load_counts_from_row(self.collection, row)
