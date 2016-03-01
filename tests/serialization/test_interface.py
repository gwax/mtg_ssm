"""Tests for mtg_ssm.serialization.interface.py"""

from mtg_ssm.mtg import collection
from mtg_ssm.mtg import models
from mtg_ssm.serialization import interface

from tests.mtgjson import mtgjson_testcase


class StubSerializer(interface.MtgSsmSerializer):
    """Stub serializer for testing purposes."""

    extensions = None
    write_to_file = None
    read_from_file = None


class LoadCountsTest(mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        self.collection = collection.Collection(self.mtg_data)
        self.print_id = '958ae1416f8f6287115ccd7c5c61f2415a313546'
        self.printing = self.collection.id_to_printing[self.print_id]
        self.serializer = StubSerializer(self.collection)

    def test_printing_not_found(self):
        counts = {}
        with self.assertRaises(interface.DeserializationError):
            self.serializer.load_counts(counts)

    def test_load_nothing(self):
        counts = {'id': self.print_id}
        self.serializer.load_counts(counts)
        self.assertFalse(self.printing.counts)

    def test_load_zeros(self):
        counts = {'id': self.print_id, 'copies': 0, 'foils': 0}
        self.serializer.load_counts(counts)
        self.assertFalse(self.printing.counts)

    def test_load_counts(self):
        counts = {'id': self.print_id, 'copies': 1, 'foils': 2}
        self.serializer.load_counts(counts)
        expected = {
            models.CountTypes.copies: 1,
            models.CountTypes.foils: 2,
        }
        self.assertEqual(expected, self.printing.counts)

    def test_increase_counts(self):
        self.printing.counts[models.CountTypes.copies] = 1
        self.printing.counts[models.CountTypes.foils] = 2
        counts = {'id': self.print_id, 'copies': 4, 'foils': 8}
        self.serializer.load_counts(counts)
        expected = {
            models.CountTypes.copies: 5,
            models.CountTypes.copies: 10,
        }
        self.assertEqual(expected, self.printing.counts)
