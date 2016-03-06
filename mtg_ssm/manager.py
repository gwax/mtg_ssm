#!/usr/bin/env python3
"""Script to manage magic collection spreadsheets."""

import argparse
import datetime
import os
import shutil

import mtg_ssm

from mtg_ssm import mtgjson
from mtg_ssm import profiling
import mtg_ssm.serialization.interface as ser_interface
from mtg_ssm.mtg import collection


MTG_SSM_DATA_PATH = os.path.expanduser(os.path.join('~', '.mtg_ssm'))


def get_args(args=None):
    """Create and return application argument parser."""
    parser = argparse.ArgumentParser(
        description='Magic Collection Spreadsheet Manager')
    parser.add_argument(
        '--version', action='version', version=mtg_ssm.__version__)

    parser.add_argument(
        '--data_path', default=MTG_SSM_DATA_PATH,
        help='Path to mtg_ssm\'s data storage folder. Default={0}'.format(
            MTG_SSM_DATA_PATH))
    parser.add_argument(
        '--include_online_only', default=False, action='store_true',
        help='Include online only sets (e.g. Masters sets) in the database.')
    parser.add_argument(
        '--profile_stats', default=False, action='store_true',
        help='Output profiling statistics.')

    format_choices = ser_interface.MtgSsmSerializer.all_formats()
    parser.add_argument(
        '--format', default='auto', choices=format_choices,
        help='File format for collection, auto will guess from the '
        'file extension.')
    parser.add_argument(
        'collection', help='Sheet to update.')

    parser.add_argument(
        '--import_format', default='auto', choices=format_choices,
        help='File format for the import file, if provided.')
    parser.add_argument(
        'imports', metavar='import', nargs='*',
        help='Optional files to read additional counts from. You may also '
        'use this to convert from one format to another. Note: counts will '
        'be added to collection, not replaced.')

    return parser.parse_args(args=args)


def build_collection(data_path, include_online_only):
    """Get a collection with current mtgjson data."""
    mtgjson.fetch_mtgjson(data_path)
    print('Reading mtgjson data.')
    mtgjsondata = mtgjson.read_mtgjson(data_path)
    return collection.Collection(
        mtgjsondata, include_online_only=include_online_only)


def process_files(args):
    """Run the requested operations."""
    coll = build_collection(args.data_path, args.include_online_only)

    for import_file in args.imports:
        _, ext = os.path.splitext(import_file)
        import_serializer_class = ser_interface.MtgSsmSerializer \
            .by_extension_and_format(ext, args.import_format)
        import_serializer = import_serializer_class(coll)
        print('Importing counts from import: %s' % import_file)
        import_serializer.read_from_file(import_file)

    _, ext = os.path.splitext(args.collection)
    serializer_class = ser_interface.MtgSsmSerializer.by_extension_and_format(
        ext, args.format)
    serializer = serializer_class(coll)

    if os.path.exists(args.collection):
        print('Reading counts from existing file.')
        serializer.read_from_file(args.collection)
        backup_name = args.collection + '.bak-{:%Y%m%d_%H%M%S}'.format(
            datetime.datetime.now())
        print('Moving existing collection to backup: %s' % backup_name)
        shutil.move(args.collection, backup_name)

    print('Writing collection to file.')
    serializer.write_to_file(args.collection)


def main():
    """Process user input and run commands.."""
    args = get_args()
    with profiling.profiled(enabled=args.profile_stats):
        process_files(args)


if __name__ == '__main__':
    main()
