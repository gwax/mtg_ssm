"""CSV serializer."""

import csv

from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface

CSV_HEADER = [
    'set',
    'name',
    'number',
    'multiverseid',
    'id',
] + [ct.name for ct in models.CountTypes]


def row_from_printing(printing):
    """Given a CardPrinting, return a csv row."""
    csv_row = {
        'set': printing.set_code,
        'name': printing.card_name,
        'number': printing.set_number,
        'multiverseid': printing.multiverseid,
        'id': printing.id_,
    }
    for counttype, count in printing.counts.items():
        if count:
            csv_row[counttype.name] = count
    return csv_row


def csv_rows_from_collection(collection):
    """Generator that yields csv rows from a collection."""
    for card_set in collection.card_sets:
        for printing in card_set.printings:
            yield row_from_printing(printing)


class MtgCsvSerializer(interface.MtgSsmSerializer):
    """MtgSsmSerializer for reading and writing csv files."""

    format = 'csv'
    extension = 'csv'

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
                self.load_counts(row)
