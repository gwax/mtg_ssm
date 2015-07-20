#!/usr/bin/env python3
"""Script to help manage magic collection database."""

import argparse
import os

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo

from mtgcdb import manager_helper
from mtgcdb import profiling


MTGCDB_DATA_PATH = os.path.expanduser(os.path.join('~', '.mtgcdb'))
MTGCDB_SQLITE_FILENAME = 'collection.sqlite'


def get_parser():
    """Create and return application argument parser."""
    parser = argparse.ArgumentParser(
        description='Magic collection database manager.')
    parser.add_argument(
        '--data_path', default=MTGCDB_DATA_PATH, help=(
            'Path to mtgcdb\'s data storage folder. Default={0}'.format(
                MTGCDB_DATA_PATH)))
    parser.add_argument(
        '--db_url', default=None, help=(
            'SQLAlchemy style database URL for mtgcdb collection database. '
            'Defaults to using sqlite:///DATA_PATH/{0}'.format(
                MTGCDB_SQLITE_FILENAME)))
    parser.add_argument(
        '--debug_stats', default=False, action='store_true', help=(
            'Output additional debugging statistics.'))

    cmd_subparser = parser.add_subparsers(dest='command', help=(
        'The collection operation to perform.'))
    cmd_subparser.required = True

    uc_parser = cmd_subparser.add_parser('update_cards', help=(
        'Check for and download a new version of mtgjson and then update '
        'cards and sets in the database. All card counts in the database '
        'will be preserved.'))
    uc_parser.add_argument(
        '--include_online_only', default=False, action='store_true', help=(
            'Include online only sets (e.g. Masters sets) in the database.'))

    wcsv_parser = cmd_subparser.add_parser('write_csv', help=(
        'Write all cards from the database to a CSV file. If a file already '
        'exists at the target location, a backup will be created and the '
        'existing file will be replaced. All counts will be taken from the '
        'database, ignoring any counts in existing CSV files.'))
    wcsv_parser.add_argument('csv_filename', help=(
        'The path and filename for the target CSV file.'))

    rcsv_parser = cmd_subparser.add_parser('read_csv', help=(
        'Read card counts from a CSV file into the database. All existing '
        'counts in the database will be overwritten. NOTE: Database backups '
        'are NOT performed.'))
    rcsv_parser.add_argument('csv_filename', help=(
        'The path and filename for the source CSV file.'))

    ucsv_parser = cmd_subparser.add_parser('update_csv', help=(
        'Update cards from mtgjson, read counts from CSV file, and write '
        'updated cards back to CSV file. The original CSV file will be backed '
        'up. NOTE: Database counts are NOT backed up and will be overwritten '
        'by CSV contents.'))
    ucsv_parser.add_argument(
        '--include_online_only', default=False, action='store_true', help=(
            'Include online only sets (e.g. Masters sets) in the database.'))
    ucsv_parser.add_argument('csv_filename', help=(
        'The path and filename for the target CSV file.'))

    wxlsx_parser = cmd_subparser.add_parser('write_xlsx', help=(
        'Write all cards from the database to an Office Open XML XLSX '
        'spreadsheet. If a file already exists at the target location, a '
        'backup will be created and the existing file will be replaced. All '
        'counts will be taken from the database, ignoring any counts in '
        'existing XLSX files.'))
    wxlsx_parser.add_argument('xlsx_filename', help=(
        'The path and filename for the target XLSX file.'))

    rxlsx_parser = cmd_subparser.add_parser('read_xlsx', help=(
        'Read card counts from an Office Open XML XLSX spreadsheet. All '
        'existing counts in the database will be overwritten. NOTE: Database '
        'backups are NOT performed.'))
    rxlsx_parser.add_argument('xlsx_filename', help=(
        'The path and filename of the source XLSX file.'))

    uxlsx_parser = cmd_subparser.add_parser('update_xlsx', help=(
        'Update cards from mtgjson, read counts from an Open Office XML XLSX '
        'spreadsheet, and write updated cards back to XLSX file. The original '
        'XLSX file will be backed up. NOTE: Database counts are not backed up '
        'and will be overwritten by XLSX contents.'))
    uxlsx_parser.add_argument(
        '--include_online_only', default=False, action='store_true', help=(
            'Include online only sets (e.g. Masters sets) in the database.'))
    uxlsx_parser.add_argument('xlsx_filename', help=(
        'The path and filename for the target XLSX file.'))


    return parser


def run_commands(session_factory, args):
    session = session_factory()
    try:
        if args.command in {'update_cards', 'update_csv', 'update_xlsx'}:
            manager_helper.read_mtgjson(
                session, args.data_path, args.include_online_only)

        if args.command in {'read_csv', 'update_csv'}:
            manager_helper.read_csv(session, args.csv_filename)
        if args.command in {'read_xlsx', 'update_xlsx'}:
            manager_helper.read_xlsx(session, args.xlsx_filename)

        if args.command in {'write_csv', 'update_csv'}:
            manager_helper.write_csv(session, args.csv_filename)
        if args.command in {'write_xlsx', 'update_xlsx'}:
            manager_helper.write_xlsx(session, args.xlsx_filename)

        commit_cmds = {
            'update_cards', 'read_csv', 'read_xlsx', 'update_csv',
            'update_xlsx'}
        if args.command in commit_cmds:
            print('Committing changes to database.')
            session.commit()
    except:
        print('An error occurred, rolling back database changes.')
        session.rollback()
        raise
    finally:
        session.close()


def main():
    """Run the requested operations."""
    parser = get_parser()
    args = parser.parse_args()
    if not os.path.exists(args.data_path):
        os.makedirs(args.data_path)
    elif not os.path.isdir(args.data_path):
        raise Exception(
            'data_path: {} must be a folder'.format(args.data_path))
    db_url = args.db_url
    if db_url is None:
        db_path = os.path.join(args.data_path, MTGCDB_SQLITE_FILENAME)
        db_url = 'sqlite:///{0}'.format(db_path)
    engine = sqla.create_engine(db_url)
    session_factory = sqlo.sessionmaker(engine)
    profiler = None
    if args.debug_stats:
        profiler = profiling.start()
    try:
        run_commands(session_factory, args)
    finally:
        if profiler is not None:
            profiling.finish(profiler)


if __name__ == '__main__':
    main()
