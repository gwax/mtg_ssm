"""Script for managing mtg_ssm."""

import csv
import datetime
import os
import shutil

import openpyxl

from mtg_ssm.mtgjson import downloader
from mtg_ssm.serialization import mtgcsv
from mtg_ssm.serialization import mtgxlsx


def backup_file(filename):
    """Given a filename, backup the file if it exists."""
    if os.path.exists(filename):
        print('Target already exists, making backup.')
        backup_filename = '{0}.bak-{1:%Y-%m-%d_%H-%M-%S}'.format(
            filename, datetime.datetime.now())
        shutil.copyfile(filename, backup_filename)
        print('Backup written to {0}'.format(backup_filename))


def read_mtgjson(collection, data_path, include_online_only):
    """Read card data from mtgjson to database."""
    print('Attempting to fetch latest mtgjson.')
    new_version = downloader.fetch_mtgjson(data_path)
    if new_version:
        print('Fetched new version of mtgjson.')
    else:
        print('Latest version already present locally.')
    print('Reading mtgjson data from file.')
    mtgdata = downloader.read_mtgjson(data_path)
    print('Updating card information in database.')
    collection.load_mtg_json(mtgdata, include_online_only)
    collection.rebuild_indexes()
    collection.sort_indexes()
    print('Done updating cards in database.')


def read_csv(collection, csv_filename):
    """Read card counts from csv file to the database."""
    print('Reading card counts from csv file: {0}'.format(csv_filename))
    with open(csv_filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        mtgcsv.read_row_counts(collection, reader)
    print('Done reading counts from csv file.')


def write_csv(collection, csv_filename):
    """Write database contents to a csv file."""
    backup_file(csv_filename)
    print('Writing database contents to csv file: {0}'.format(csv_filename))
    with open(csv_filename, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, mtgcsv.header())
        writer.writeheader()
        for row in mtgcsv.dump_rows(collection):
            writer.writerow(row)
    print('Done writing database contents to csv file.')


def read_xlsx(collection, xlsx_filename):
    """Read card counts from xlsx file to the database."""
    print('Reading card counts from xlsx file: {0}'.format(xlsx_filename))
    workbook = openpyxl.load_workbook(filename=xlsx_filename, read_only=True)
    mtgxlsx.read_workbook_counts(collection, workbook)
    print('Done reading counts from xlsx file.')


def write_xlsx(collection, xlsx_filename):
    """Write database contents to xlsx file."""
    backup_file(xlsx_filename)
    print('Creating workbook with database contents.')
    workbook = mtgxlsx.dump_workbook(collection)
    print('Writing workbook to xlsx file: {0}'.format(xlsx_filename))
    workbook.save(xlsx_filename)
    print('Done writing database contents to xlsx file.')
