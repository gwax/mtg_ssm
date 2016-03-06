"""Tests for mtg_ssm.manager"""

import argparse as ap
import datetime
import os
import tempfile as tf
import unittest
from unittest import mock

from mtg_ssm import manager
from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models

from tests.mtgjson import mtgjson_testcase


class GetArgsTest(unittest.TestCase):

    def test_defaults(self):
        cmdline = 'testfilename'
        args = manager.get_args(args=cmdline.split())
        expected = ap.Namespace(
            collection='testfilename',
            format='auto',
            imports=[],
            import_format='auto',
            data_path=mock.ANY,
            include_online_only=False,
            profile_stats=False)
        self.assertEqual(expected, args)

    def test_non_default(self):
        cmdline = (
            '--data_path=/foo --include_online_only --profile_stats '
            '--format csv --import_format xlsx testfilename testfilename2')
        args = manager.get_args(args=cmdline.split())
        expected = ap.Namespace(
            collection='testfilename',
            format='csv',
            imports=['testfilename2'],
            import_format='xlsx',
            data_path='/foo',
            include_online_only=True,
            profile_stats=True)
        self.assertEqual(expected, args)

    def test_multiple_imports(self):
        cmdline = 'testfilename testfilename2 testfilename3'
        args = manager.get_args(args=cmdline.split())
        expected = ap.Namespace(
            collection='testfilename',
            format='auto',
            imports=['testfilename2', 'testfilename3'],
            import_format='auto',
            data_path=mock.ANY,
            include_online_only=False,
            profile_stats=False)
        self.assertEqual(expected, args)


class ProcessFilesTest(mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        set_data = {'MMA': self.mtg_data['MMA'], 'pMGD': self.mtg_data['pMGD']}
        self.collection = collection.Collection(set_data)
        self.print_id = 'fc46a4b72d216117a352f59217a84d0baeaaacb7'
        self.printing = self.collection.id_to_printing[self.print_id]

        patcher = mock.patch.object(manager, 'build_collection')
        self.mock_build_collection = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_build_collection.return_value = self.collection

        patcher = mock.patch.object(manager, 'datetime')
        self.mock_datetime = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_datetime.datetime.now.return_value = datetime.datetime(  # pylint: disable=no-member
            2015, 6, 28)

    def test_process_files_new(self):
        # Setup
        self.printing.counts[models.CountTypes.copies] = 2
        self.printing.counts[models.CountTypes.foils] = 5
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
            with open(outfilename, 'r') as outfile:
                outdata = outfile.readlines()
        expected = [
            # pylint: disable=line-too-long
            'set,name,number,multiverseid,id,copies,foils\n',
            'pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,\n',
            'MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,2,5\n',
        ]
        self.assertEqual(expected, outdata)

    def test_process_files_upgrade(self):
        # Setup
        with tf.TemporaryDirectory() as tmpdirname:
            infilename = os.path.join(tmpdirname, 'infile.csv')
            with open(infilename, 'w') as infile:
                infile.write(
                    'id,copies,foils\n'
                    'fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n')

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
            expected = [
                'infile.csv',
                'infile.csv.bak-20150628_000000',
            ]
            self.assertCountEqual(expected, files)

            with open(infilename, 'r') as outfile:
                outfiledata = outfile.readlines()
            with open(infilename + '.bak-20150628_000000', 'r') as bakfile:
                bakfiledata = bakfile.readlines()
        outexpected = [
            # pylint: disable=line-too-long
            'set,name,number,multiverseid,id,copies,foils\n',
            'pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,\n',
            'MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n',
        ]
        self.assertEqual(outexpected, outfiledata)
        bakexpected = [
            'id,copies,foils\n',
            'fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n',
        ]
        self.assertEqual(bakexpected, bakfiledata)

    def test_import(self):
        # Setup
        with tf.TemporaryDirectory() as tmpdirname:
            outfilename = os.path.join(tmpdirname, 'outfile.csv')
            importname = os.path.join(tmpdirname, 'import.csv')
            with open(importname, 'w') as importfile:
                importfile.write(
                    'id,copies,foils\n'
                    'fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n')

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
            expected = [
                'import.csv',
                'outfile.csv',
            ]
            self.assertCountEqual(expected, files)

            with open(outfilename, 'r') as outfile:
                outfiledata = outfile.readlines()
            with open(importname, 'r') as importfile:
                importdata = importfile.readlines()
        outexpected = [
            # pylint: disable=line-too-long
            'set,name,number,multiverseid,id,copies,foils\n',
            'pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,\n',
            'MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n',
        ]
        self.assertEqual(outexpected, outfiledata)
        importexpected = [
            'id,copies,foils\n',
            'fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8\n',
        ]
        self.assertEqual(importexpected, importdata)

    def test_multiple_import(self):
        # Setup
        with tf.TemporaryDirectory() as tmpdirname:
            outfilename = os.path.join(tmpdirname, 'outfile.csv')
            importname1 = os.path.join(tmpdirname, 'import1.csv')
            importname2 = os.path.join(tmpdirname, 'import2.csv')
            for filename in [outfilename, importname1, importname2]:
                with open(filename, 'w') as inputfile:
                    inputfile.write(
                        'id,copies,foils\n'
                        'fc46a4b72d216117a352f59217a84d0baeaaacb7,1,3\n')

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
            expected = [
                'outfile.csv',
                'outfile.csv.bak-20150628_000000',
                'import1.csv',
                'import2.csv',
            ]
            self.assertCountEqual(expected, files)

            with open(outfilename, 'r') as outfile:
                outfiledata = outfile.readlines()
        outexpected = [
            # pylint: disable=line-too-long
            'set,name,number,multiverseid,id,copies,foils\n',
            'pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,\n',
            'MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,3,9\n',
        ]
        self.assertEqual(outexpected, outfiledata)
