"""Tests for mtg_ssm.serialization.csv."""

import os
import tempfile
import textwrap

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models
from mtg_ssm.serialization import csv

from tests.mtgjson import mtgjson_testcase


class CsvSerializerTest(mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        set_data = {'MMA': self.mtg_data['MMA'], 'pMGD': self.mtg_data['pMGD']}
        self.collection = collection.Collection(set_data)
        self.print_id = 'fc46a4b72d216117a352f59217a84d0baeaaacb7'
        self.printing = self.collection.id_to_printing[self.print_id]

    def test_header(self):
        # Verify
        expected = [
            'set',
            'name',
            'number',
            'multiverseid',
            'id',
            'copies',
            'foils',
        ]
        self.assertEqual(expected, csv.CSV_HEADER)

    def test_row_from_printing(self):
        # Setup
        self.printing.counts[models.CountTypes.copies] = 3
        self.printing.counts[models.CountTypes.foils] = 5
        # Execute
        csv_row = csv.row_from_printing(self.printing)
        # Verify
        expected = {
            'set': 'MMA',
            'name': 'Thallid',
            'number': '167',
            'multiverseid': 370352,
            'id': 'fc46a4b72d216117a352f59217a84d0baeaaacb7',
            'copies': 3,
            'foils': 5,
        }
        self.assertEqual(expected, csv_row)

    def test_rows_from_collection(self):
        # Execute
        row_generator = csv.csv_rows_from_collection(self.collection)
        # Verify
        rows = list(row_generator)
        expected = [
            {
                'set': 'pMGD',
                'name': "Black Sun's Zenith",
                'number': '7',
                'multiverseid': None,
                'id': '6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc',
            },
            {
                'set': 'MMA',
                'name': 'Thallid',
                'number': '167',
                'multiverseid': 370352,
                'id': 'fc46a4b72d216117a352f59217a84d0baeaaacb7',
            },
        ]
        self.assertEqual(expected, rows)

    def test_write_to_file(self):
        # Setup
        self.printing.counts[models.CountTypes.copies] = 1
        self.printing.counts[models.CountTypes.foils] = 12
        serializer = csv.MtgCsvSerializer(self.collection)
        with tempfile.TemporaryDirectory() as tmpdirname:
            csvfilename = os.path.join(tmpdirname, 'outfile.csv')

            # Execute
            serializer.write_to_file(csvfilename)

            # Verify
            with open(csvfilename, 'r') as csvfile:
                csvdata = csvfile.read()
        expected = textwrap.dedent("""\
            set,name,number,multiverseid,id,copies,foils
            pMGD,Black Sun\'s Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
            MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,1,12
            """)
        self.assertEqual(expected, csvdata)

    def test_read_from_file(self):
        # Setup
        with tempfile.NamedTemporaryFile('w') as csvfile:
            csvfile.write(textwrap.dedent("""\
                set,name,number,multiverseid,id,copies,foils
                MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,3,72
                """))
            csvfile.flush()
            serializer = csv.MtgCsvSerializer(self.collection)

            # Execute
            serializer.read_from_file(csvfile.name)

        # Verify
        self.assertEqual(3, self.printing.counts[models.CountTypes.copies])
        self.assertEqual(72, self.printing.counts[models.CountTypes.foils])
