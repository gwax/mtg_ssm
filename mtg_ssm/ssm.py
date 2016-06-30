#!/usr/bin/env python3
"""Script for managing magic card spreadsheets."""

import argparse
import os

import mtg_ssm

import mtg_ssm.serialization.interface as ser_interface


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
        '--profile-stats', default=False, action='store_true',
        help='Output profiling statistics (for debugging)')

    parser.add_argument(
        '-d', '--dialect', nargs=2, metavar=('EXTENSION', 'DIALECT'),
        action='append', default=[],
        help='Mapping of file extensions to serializer dialects. '
             'May be repeated for multiple different extensions.')

    # Commands
    subparsers = parser.add_subparsers(
        dest='action', title='actions')
    subparsers.required = True

    create = subparsers.add_parser(
        'create', aliases=['c'],
        help='Create a new, empty collection spreadsheet')
    create.set_defaults(func=print)
    create.add_argument(
        'collection', help='Filename for the new collection')

    update = subparsers.add_parser(
        'update', aliases=['u'],
        help='Update cards in a collection spreadsheet, preserving counts')
    update.set_defaults(func=print)
    update.add_argument(
        'collection', help='Filename for the collection to update')

    merge = subparsers.add_parser(
        'merge', aliases=['m'],
        help='Merge one or more collection spreadsheets into another. May '
        'also be used for format conversions.')
    merge.set_defaults(func=print)
    merge.add_argument(
        'collection', help='Filename for the target collection')
    merge.add_argument(
        'imports', nargs='+',
        help='Filename(s) for collection(s) to import/merge counts from')

    diff = subparsers.add_parser(
        'diff', aliases=['d'],
        help='Create a collection from the differences between two other '
        'collections')
    diff.set_defaults(func=print)
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


def main():
    args = get_args()
    args.func(args)


if __name__ == '__main__':
    main()
