"""Tests for mtg_ssm.manager"""

import argparse as ap
import datetime
import os
import tempfile as tf
import textwrap
from unittest import mock

import pytest

from mtg_ssm import manager
from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models


@pytest.mark.parametrize('cmdline,expected', [
    (
        'testfilename',
        ap.Namespace(
            collection='testfilename',
            format='auto',
            imports=[],
            import_format='auto',
            data_path=mock.ANY,
            include_online_only=False,
            profile_stats=False)
    ), (
        '--data_path=/foo --include_online_only --profile_stats '
        '--format csv --import_format xlsx testfilename testfilename2',
        ap.Namespace(
            collection='testfilename',
            format='csv',
            imports=['testfilename2'],
            import_format='xlsx',
            data_path='/foo',
            include_online_only=True,
            profile_stats=True)
    ), (
        'testfilename testfilename2 testfilename3',
        ap.Namespace(
            collection='testfilename',
            format='auto',
            imports=['testfilename2', 'testfilename3'],
            import_format='auto',
            data_path=mock.ANY,
            include_online_only=False,
            profile_stats=False)
    )
])
def test_get_args(cmdline, expected):
    args = manager.get_args(args=cmdline.split())
    assert args == expected

TEST_PRINT_ID = 'fc46a4b72d216117a352f59217a84d0baeaaacb7'


@pytest.fixture
def coll(sets_data):
    sets_data = {k: v for k, v in sets_data.items() if k in {'MMA', 'pMGD'}}
    return collection.Collection(sets_data)


@pytest.fixture
def printing(coll):
    return coll.id_to_printing[TEST_PRINT_ID]


@pytest.fixture(autouse=True)
def patch_now_and_build_collection(monkeypatch, coll):
    class mock_datetime(datetime.datetime):
        @classmethod
        def now(cls, *_):
            return datetime.datetime(2015, 6, 28)
    monkeypatch.setattr(datetime, 'datetime', mock_datetime)

    def mock_build_collection(*_):
        return coll
    monkeypatch.setattr(manager, 'build_collection', mock_build_collection)


def test_process_files_new(coll, printing):
    # Setup
    printing.counts[models.CountTypes.copies] = 2
    printing.counts[models.CountTypes.foils] = 5
    with tf.TemporaryDirectory() as tmpdirname:
        outfilename = os.path.join(tmpdirname, 'outfile.csv')
        args = ap.Namespace(
            collection=outfilename,
            format='auto',
            imports=[],
            import_format='auto',
            data_path=mock.sentinel.data_path,
            include_online_only=mock.sentinel.include_online_only)

        # Execute
        manager.process_files(args)

        # Verify
        with open(outfilename, 'rt') as outfile:
            outdata = outfile.read()
    expected = textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,2,5
    """)
    assert outdata == expected


def test_process_files_upgrade(coll):
    # Setup
    with tf.TemporaryDirectory() as tmpdirname:
        infilename = os.path.join(tmpdirname, 'infile.csv')
        with open(infilename, 'wt') as infile:
            infile.write(textwrap.dedent("""\
                id,copies,foils
                fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
            """))

        args = ap.Namespace(
            collection=infilename,
            format='auto',
            imports=[],
            import_format='auto',
            data_path=mock.sentinel.data_path,
            include_online_only=mock.sentinel.include_online_only)

        # Execute
        manager.process_files(args)

        # Verify
        files = os.listdir(tmpdirname)
        expected = {
            'infile.csv',
            'infile.csv.bak-20150628_000000',
        }
        assert set(files) == expected

        with open(infilename, 'rt') as outfile:
            outfiledata = outfile.read()
        with open(infilename + '.bak-20150628_000000', 'rt') as bakfile:
            bakfiledata = bakfile.read()
    outexpected = textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
    """)
    assert outfiledata == outexpected
    bakexpected = textwrap.dedent("""\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
    """)
    assert bakfiledata == bakexpected


def test_import(coll):
    # Setup
    with tf.TemporaryDirectory() as tmpdirname:
        outfilename = os.path.join(tmpdirname, 'outfile.csv')
        importname = os.path.join(tmpdirname, 'import.csv')
        with open(importname, 'wt') as importfile:
            importfile.write(textwrap.dedent("""\
                id,copies,foils
                fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
            """))

        args = ap.Namespace(
            collection=outfilename,
            format='auto',
            imports=[importname],
            import_format='auto',
            data_path=mock.sentinel.data_path,
            include_online_only=mock.sentinel.include_online_only)

        # Execute
        manager.process_files(args)

        # Verify
        files = os.listdir(tmpdirname)
        expected = {
            'import.csv',
            'outfile.csv',
        }
        assert set(files) == expected

        with open(outfilename, 'rt') as outfile:
            outfiledata = outfile.read()
        with open(importname, 'rt') as importfile:
            importdata = importfile.read()
    outexpected = textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
    """)
    assert outfiledata == outexpected
    importexpected = textwrap.dedent("""\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
    """)
    assert importdata == importexpected


def test_multiple_import(coll):
    # Setup
    with tf.TemporaryDirectory() as tmpdirname:
        outfilename = os.path.join(tmpdirname, 'outfile.csv')
        importname1 = os.path.join(tmpdirname, 'import1.csv')
        importname2 = os.path.join(tmpdirname, 'import2.csv')
        for filename in [outfilename, importname1, importname2]:
            with open(filename, 'wt') as inputfile:
                inputfile.write(textwrap.dedent("""\
                    id,copies,foils
                    fc46a4b72d216117a352f59217a84d0baeaaacb7,1,3
                """))

        args = ap.Namespace(
            collection=outfilename,
            format='auto',
            imports=[importname1, importname2],
            import_format='auto',
            data_path=mock.sentinel.data_path,
            include_online_only=mock.sentinel.include_online_only)

        # Execute
        manager.process_files(args)

        # Verify
        files = os.listdir(tmpdirname)
        expected = {
            'outfile.csv',
            'outfile.csv.bak-20150628_000000',
            'import1.csv',
            'import2.csv',
        }
        assert set(files) == expected

        with open(outfilename, 'rt') as outfile:
            outfiledata = outfile.read()
    outexpected = textwrap.dedent("""\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,3,9
    """)
    assert outfiledata == outexpected
