#!/usr/bin/env python3
"""Script to manage magic collection spreadsheets."""

import argparse
import datetime as dt
import os
import shutil
import sys

import mtg_ssm

from mtg_ssm import profiling
import mtg_ssm.serialization.interface as ser_interface
from mtg_ssm.mtg import collection
from mtg_ssm.mtgjson import downloader


MTG_SSM_DATA_PATH = os.path.expanduser(os.path.join('~', '.mtg_ssm'))


def get_args():
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
        '-f', '--format', default='auto', choices=format_choices,
        help='File format for collection, auto will guess from the '
        'file extension.')

    parser.add_argument(
        'collection', help='Sheet to update.')

    return parser.parse_args()


def build_collection(data_path, include_online_only):
    """Get a collection with current mtgjson data."""
    downloader.fetch_mtgjson(data_path)
    print('Reading mtgjson data.')
    mtgjson = downloader.read_mtgjson(data_path)
    return collection.Collection(
        mtgjson, include_online_only=include_online_only)


def process_files(args):
    """Run the requested operations."""
    _, ext = os.path.splitext(args.collection)
    serializer_class = ser_interface.MtgSsmSerializer.by_extension_and_format(
        ext, args.format)

    coll = build_collection(args.data_path, args.include_online_only)
    serializer = serializer_class(coll)

    if os.path.exists(args.collection):
        print('Reading counts from existing file.')
        serializer.read_from_file(args.collection)
        backup_name = args.collection + '.bak-{:%Y%m%d_%H%M%S}'.format(
            dt.datetime.now())
        print('Moving existing collection to backup: %s' % backup_name)
        shutil.move(args.collection, backup_name)

    print('Writing collection to file.')
    serializer.write_to_file(args.collection)


def main():
    """Process user input and run commands.."""
    args = get_args()
    if not os.path.exists(args.data_path):
        os.makedirs(args.data_path)
    elif not os.path.isdir(args.data_path):
        raise Exception(
            'data_path: {} must be a folder'.format(args.data_path))

    profiler = None
    if args.profile_stats:
        profiler = profiling.start()
    try:
        process_files(args)
    finally:
        if profiler is not None:
            profiling.finish(profiler)


if __name__ == '__main__':
    main()
