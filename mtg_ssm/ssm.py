#!/usr/bin/env python3
"""Script for managing magic card spreadsheets."""

import argparse
import datetime
import os
import shutil
import tempfile

import mtg_ssm

from mtg_ssm import mtgjson
import mtg_ssm.serialization.interface as ser_interface
from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts


DEFAULT_DATA_PATH = os.path.expanduser(os.path.join('~', '.mtg_ssm'))


def epilog():
    """Generate the argparse help epilog with dialect descriptions."""
    dialect_docs = 'available dialects:\n'
    ext_dia_desc = ser_interface.SerializationDialect.dialects()
    for extension, dialect, description in ext_dia_desc:
        dialect_docs += '  {ext:<8} {dia:<12} {desc}\n'.format(
            ext=extension, dia=dialect, desc=description)
    return dialect_docs


def get_args(args=None):
    """Parse and return application arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Magic collection Spreadsheet Manager',
        epilog=epilog())
    parser.add_argument(
        '--version', action='version', version=mtg_ssm.__version__)

    parser.add_argument(
        '--data-path', default=DEFAULT_DATA_PATH,
        help='Path to mtg_ssm\'s data storage folder. Default={}'.format(
            DEFAULT_DATA_PATH))
    parser.add_argument(
        '--include-online-only', default=False, action='store_true',
        help='Include online only sets (e.g. Masters sets)')

    parser.add_argument(
        '-d', '--dialect', nargs=2, metavar=('EXTENSION', 'DIALECT'),
        action='append', default=[],
        help='Mapping of file extensions to serializer dialects. '
             'May be repeated for multiple different extensions.')

    # Commands
    subparsers = parser.add_subparsers(dest='action', title='actions')
    subparsers.required = True

    create = subparsers.add_parser(
        'create', aliases=['c'],
        help='Create a new, empty collection spreadsheet')
    create.set_defaults(func=create_cmd)
    create.add_argument(
        'collection', help='Filename for the new collection')

    update = subparsers.add_parser(
        'update', aliases=['u'],
        help='Update cards in a collection spreadsheet, preserving counts')
    update.set_defaults(func=update_cmd)
    update.add_argument(
        'collection', help='Filename for the collection to update')

    merge = subparsers.add_parser(
        'merge', aliases=['m'],
        help='Merge one or more collection spreadsheets into another. May '
        'also be used for format conversions.')
    merge.set_defaults(func=merge_cmd)
    merge.add_argument(
        'collection', help='Filename for the target collection')
    merge.add_argument(
        'imports', nargs='+',
        help='Filename(s) for collection(s) to import/merge counts from')

    diff = subparsers.add_parser(
        'diff', aliases=['d'],
        help='Create a collection from the differences between two other '
        'collections')
    diff.set_defaults(func=diff_cmd)
    diff.add_argument(
        'left',
        help='Filename for first collection to diff (positive counts)')
    diff.add_argument(
        'right',
        help='Filename for second collection to diff (negative counts)')
    diff.add_argument(
        'output', help='Filename for result collection of diff')

    parsed_args = parser.parse_args(args=args)
    parsed_args.dialect = dict(parsed_args.dialect)
    return parsed_args


def build_card_db(data_path, include_online_only):
    """Get a card_db with current mtgjson data."""
    try:
        mtgjson.fetch_mtgjson(data_path)
    except mtgjson.DownloadError:
        print('Failed to fetch mtgjson data, attempting to use cached data.')
    print('Reading mtgjson data.')
    mtgjsondata = mtgjson.read_mtgjson(data_path)
    return card_db.CardDb(
        mtgjsondata, include_online_only=include_online_only)


def get_serializer(cdb, dialect_mapping, filename):
    """Retrieve a serializer compatible with a given filename."""
    _, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')
    serialization_class = ser_interface.SerializationDialect.by_extension(
        extension, dialect_mapping)
    return serialization_class(cdb)


def get_backup_name(filename):
    """Given a filename, return a timestamped backup name for the file."""
    basename, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')
    now = datetime.datetime.now()
    return '{basename}.{now:%Y%m%d_%H%M%S}.{extension}'.format(
        basename=basename, now=now, extension=extension)


def write_file(serializer, print_counts, filename):
    """Write print counts to a file, backing up existing target files."""
    if not os.path.exists(filename):
        print('Writing collection to file: ' + filename)
        serializer.write(filename, print_counts)
    else:
        backup_name = get_backup_name(filename)
        with tempfile.NamedTemporaryFile() as temp_coll:
            print('Writing to temporary file.')
            serializer.write(temp_coll.name, print_counts)
            print('Backing up exiting file to: ' + backup_name)
            shutil.copy(filename, backup_name)
            print('Overwriting with new collection: ' + filename)
            shutil.copy(temp_coll.name, filename)


def create_cmd(args):
    """Create a new, empty collection."""
    cdb = build_card_db(args.data_path, args.include_online_only)
    serializer = get_serializer(cdb, args.dialect, args.collection)
    write_file(serializer, {}, args.collection)


def update_cmd(args):
    """Update an existing collection, preserving counts."""
    cdb = build_card_db(args.data_path, args.include_online_only)
    serializer = get_serializer(cdb, args.dialect, args.collection)
    print('Reading counts from ' + args.collection)
    print_counts = serializer.read(args.collection)
    write_file(serializer, print_counts, args.collection)


def merge_cmd(args):
    """Merge counts from one or more inputs into a new/existing collection."""
    cdb = build_card_db(args.data_path, args.include_online_only)
    coll_serializer = get_serializer(cdb, args.dialect, args.collection)
    print_counts = counts.new_print_counts()
    if os.path.exists(args.collection):
        print('Reading counts from ' + args.collection)
        print_counts = coll_serializer.read(args.collection)
    for import_file in args.imports:
        input_serializer = get_serializer(cdb, args.dialect, import_file)
        print('Merging counts from ' + import_file)
        print_counts = counts.merge_print_counts(
            print_counts, input_serializer.read(import_file))
    write_file(coll_serializer, print_counts, args.collection)


def diff_cmd(args):
    """Diff two collections, putting the output in a third."""
    cdb = build_card_db(args.data_path, args.include_online_only)
    left_serializer = get_serializer(cdb, args.dialect, args.left)
    right_serializer = get_serializer(cdb, args.dialect, args.right)
    output_serializer = get_serializer(cdb, args.dialect, args.output)
    print('Diffing counts between %s and %s' % (args.left, args.right))
    print_counts = counts.diff_print_counts(
        left_serializer.read(args.left),
        right_serializer.read(args.right))
    write_file(output_serializer, print_counts, args.output)


def main():
    """Get args and run the appropriate command."""
    args = get_args()
    args.func(args)


if __name__ == '__main__':
    main()
