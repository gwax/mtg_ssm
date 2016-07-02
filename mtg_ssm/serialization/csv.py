"""CSV serializer."""

import csv

from mtg_ssm.mtg import counts
from mtg_ssm.serialization import interface

CSV_HEADER = [
    'set',
    'name',
    'number',
    'multiverseid',
    'id',
] + [ct.name for ct in counts.CountTypes]


def row_for_printing(printing, printing_counts):
    """Given a CardPrinting and counts, return a csv row."""
    csv_row = {
        'set': printing.set_code,
        'name': printing.card_name,
        'number': printing.set_number,
        'multiverseid': printing.multiverseid,
        'id': printing.id_,
    }
    for counttype, count in printing_counts.items():
        if count:
            csv_row[counttype.name] = count
    return csv_row


def rows_for_printings(cdb, print_counts, verbose):
    """Generator that yields csv rows from a card_db."""
    for card_set in cdb.card_sets:
        for printing in card_set.printings:
            printing_counts = print_counts.get(printing.id_, {})
            if verbose or any(printing_counts):
                yield row_for_printing(printing, printing_counts)


class CsvFullDialect(interface.SerializationDialect):
    """csv collection writing a row for every printing"""
    extension = 'csv'
    dialect = 'csv'

    verbose = True

    def write(self, filename: str, print_counts) -> None:
        """Write print counts to a file."""
        with open(filename, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, CSV_HEADER)
            writer.writeheader()
            for row in rows_for_printings(
                    self.cdb, print_counts, self.verbose):
                writer.writerow(row)

    def read(self, filename: str):
        """Read print counts from file."""
        with open(filename, 'r') as csv_file:
            return counts.aggregate_print_counts(
                self.cdb, csv.DictReader(csv_file), strict=True)


class CsvTerseDialect(CsvFullDialect):
    """csv collection writing only rows that have counts"""
    dialect = 'terse'

    verbose = False
