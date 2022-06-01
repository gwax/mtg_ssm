#!/usr/bin/env python3
"""Script for managing magic card spreadsheets."""

import argparse
import datetime as dt
import tempfile
from pathlib import Path
from typing import Dict, List, Set

import mtg_ssm
import mtg_ssm.serialization.interface as ser_interface
from mtg_ssm.containers import bundles
from mtg_ssm.containers.collection import MagicCollection
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.scryfall import fetcher
from mtg_ssm.scryfall.models import ScrySetType


def epilog() -> str:
    """Generate the argparse help epilog with dialect descriptions."""
    dialect_docs = "available dialects:\n"
    ext_dia_desc = ser_interface.SerializationDialect.dialects()
    for extension, dialect, description in ext_dia_desc:
        dialect_docs += f"  {extension:<8} {dialect:<12} {description}\n"
    return dialect_docs


def set_type_list(value: str) -> Set[ScrySetType]:
    """Argparse type to convert a string to a set of Scryfall Set Types."""
    set_types = set()
    for set_str in value.split(","):
        try:
            set_types.add(ScrySetType(set_str))
        except ValueError as err:
            msg = (
                f"{set_str} in {value} is not a valid set_type, please use a commas separated list of values from: "
                + ", ".join(ScrySetType)
            )
            raise argparse.ArgumentTypeError(msg) from err
    return set_types


def get_args(args: List[str] = None) -> argparse.Namespace:
    """Parse and return application arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Magic collection Spreadsheet Manager",
        epilog=epilog(),
    )
    parser.add_argument("--version", action="version", version=mtg_ssm.__version__)

    parser.add_argument(
        "--include-digital",
        default=False,
        action="store_true",
        help="Include digital only sets (e.g. Vintage Masters)",
    )

    parser.add_argument(
        "-d",
        "--dialect",
        nargs=2,
        metavar=("EXTENSION", "DIALECT"),
        action="append",
        default=[],
        help="Mapping of file extensions to serializer dialects. "
        "May be repeated for multiple different extensions.",
    )

    default_set_types = set(ScrySetType) - {ScrySetType.MEMORABILIA, ScrySetType.TOKEN}
    parser.add_argument(
        "--set-types",
        default=",".join(default_set_types),
        type=set_type_list,
        help="List of set types to include as a comma separted list of values from: "
        + ", ".join(ScrySetType),
    )

    # Commands
    subparsers = parser.add_subparsers(dest="action", title="actions")
    subparsers.required = True

    create = subparsers.add_parser(
        "create", aliases=["c"], help="Create a new, empty collection spreadsheet"
    )
    create.set_defaults(func=create_cmd)
    create.add_argument("collection", type=Path, help="Filename for the new collection")

    update = subparsers.add_parser(
        "update",
        aliases=["u"],
        help="Update cards in a collection spreadsheet, preserving counts",
    )
    update.set_defaults(func=update_cmd)
    update.add_argument(
        "collection", type=Path, help="Filename for the collection to update"
    )

    merge = subparsers.add_parser(
        "merge",
        aliases=["m"],
        help="Merge one or more collection spreadsheets into another. May also be used for format conversions.",
    )
    merge.set_defaults(func=merge_cmd)
    merge.add_argument(
        "collection", type=Path, help="Filename for the target collection"
    )
    merge.add_argument(
        "imports",
        nargs="+",
        type=Path,
        help="Filename(s) for collection(s) to import/merge counts from",
    )

    diff = subparsers.add_parser(
        "diff",
        aliases=["d"],
        help="Create a collection from the differences between two other collections",
    )
    diff.set_defaults(func=diff_cmd)
    diff.add_argument(
        "left",
        type=Path,
        help="Filename for first collection to diff (positive counts)",
    )
    diff.add_argument(
        "right",
        type=Path,
        help="Filename for second collection to diff (negative counts)",
    )
    diff.add_argument(
        "output", type=Path, help="Filename for result collection of diff"
    )

    parsed_args = parser.parse_args(args=args)
    parsed_args.dialect = dict(parsed_args.dialect)
    return parsed_args


def get_oracle(set_types: Set[ScrySetType], include_digital: bool) -> Oracle:
    """Get a card_db with current mtgjson data."""
    scrydata = fetcher.scryfetch()
    scrydata = bundles.filter_set_types(scrydata, set_types)
    if not include_digital:
        scrydata = bundles.remove_digital(scrydata)
    return Oracle(scrydata)


def get_serializer(
    dialect_mapping: Dict[str, str], path: Path
) -> ser_interface.SerializationDialect:
    """Retrieve a serializer compatible with a given filename."""
    extension = path.suffix.lstrip(".")
    serialization_class = ser_interface.SerializationDialect.by_extension(
        extension, dialect_mapping
    )
    return serialization_class()


def get_backup_path(path: Path) -> Path:
    """Given a filename, return a timestamped backup name for the file."""
    now = dt.datetime.now()
    return path.parent / f"{path.stem}.{now:%Y%m%d_%H%M%S}{path.suffix}"


def write_file(
    serializer: ser_interface.SerializationDialect,
    collection: MagicCollection,
    path: Path,
) -> None:
    """Write print counts to a file, backing up existing target files."""
    if not path.exists():
        print(f"Writing collection to file: {path}")
        serializer.write(path, collection)
    else:
        backup_path = get_backup_path(path)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / path.name
            print("Writing to temporary file.")
            serializer.write(temp_path, collection)
            print(f"Backing up existing file to: {backup_path}")
            path.replace(backup_path)
            print(f"Writing collection: {path}")
            temp_path.replace(path)


def create_cmd(args: argparse.Namespace, oracle: Oracle) -> None:
    """Create a new, empty collection."""
    collection = MagicCollection(oracle=oracle, counts={})
    serializer = get_serializer(args.dialect, args.collection)
    write_file(serializer, collection, args.collection)


def update_cmd(args: argparse.Namespace, oracle: Oracle) -> None:
    """Update an existing collection, preserving counts."""
    serializer = get_serializer(args.dialect, args.collection)
    print(f"Reading counts from {args.collection}")
    collection = serializer.read(args.collection, oracle)
    write_file(serializer, collection, args.collection)


def merge_cmd(args: argparse.Namespace, oracle: Oracle) -> None:
    """Merge counts from one or more inputs into a new/existing collection."""
    coll_serializer = get_serializer(args.dialect, args.collection)
    collection = MagicCollection(oracle=oracle, counts={})
    if args.collection.exists():
        print(f"Reading counts from {args.collection}")
        collection = coll_serializer.read(args.collection, oracle)
    for import_path in args.imports:
        input_serializer = get_serializer(args.dialect, import_path)
        print(f"Merging counts from {import_path}")
        collection += input_serializer.read(import_path, oracle)
    write_file(coll_serializer, collection, args.collection)


def diff_cmd(args: argparse.Namespace, oracle: Oracle) -> None:
    """Diff two collections, putting the output in a third."""
    left_serializer = get_serializer(args.dialect, args.left)
    right_serializer = get_serializer(args.dialect, args.right)
    output_serializer = get_serializer(args.dialect, args.output)
    print(f"Diffing counts between {args.left} and {args.right}")
    diff_collection = left_serializer.read(args.left, oracle) - right_serializer.read(
        args.right, oracle
    )
    write_file(output_serializer, diff_collection, args.output)


def main() -> None:
    """Get args and run the appropriate command."""
    args = get_args()
    oracle = get_oracle(args.set_types, args.include_digital)
    args.func(args, oracle)


if __name__ == "__main__":
    main()
