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


def row_for_printing(printing, print_counts):
    """Given a CardPrinting and counts, return a csv row."""
    csv_row = {
        'set': printing.set_code,
        'name': printing.card_name,
        'number': printing.set_number,
        'multiverseid': printing.multiverseid,
        'id': printing.id_,
    }
    for counttype, count in print_counts.get(printing, {}).items():
        if count:
            csv_row[counttype.name] = count
    return csv_row


def rows_for_printings(cdb, print_counts):
    """Generator that yields csv rows from a card_db."""
    for card_set in cdb.card_sets:
        for printing in card_set.printings:
            yield row_for_printing(printing, print_counts)


class MtgCsvSerializer(interface.MtgSsmSerializer):
    """MtgSsmSerializer for reading and writing csv files."""

    format = 'csv'
    extension = 'csv'

    def write(self, filename: str, print_counts) -> None:
        """Write print counts to a file."""
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, CSV_HEADER)
            writer.writeheader()
            for row in rows_for_printings(self.cdb, print_counts):
                writer.writerow(row)

    def read(self, filename: str):
        """Read print counts from file."""
        with open(filename, 'r') as csv_file:
            return interface.build_print_counts(
                self.cdb, csv.DictReader(csv_file))
