"""Tests for mtg_ssm.mtgcsv"""

from mtg_ssm.db import models
from mtg_ssm.mtgjson import mtgjson
from mtg_ssm.serialization import mtgdict

from tests.mtgjson import mtgjson_testcase
from tests.db import sqlite_testcase


class MtgDictTest(
        sqlite_testcase.SqliteTestCase, mtgjson_testcase.MtgJsonTestCase):

    def setUp(self):
        super().setUp()
        connection = self.engine.connect()
        models.Base.metadata.create_all(connection)
        connection.close()

    def test_get_printing_not_found(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing']}

        card_dict = {}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_set_name_num(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing']}

        card_dict = {'set': 'SET', 'name': 'NAME', 'number': 'NUM'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertEqual('printing', printing)

    def test_get_printing_set_name_num_duplicate(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing', 'p2']}

        card_dict = {'set': 'SET', 'name': 'NAME', 'number': 'NUM'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_set_name_mv(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing']}

        card_dict = {'set': 'SET', 'name': 'NAME', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertEqual('printing', printing)

    def test_get_printing_set_name_mv_duplicate(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing', 'p2']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing']}

        card_dict = {'set': 'SET', 'name': 'NAME', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_set_name_num_mv(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {
            ('SET', 'NAME', 'MV'): ['printing', 'p2', 'p3']}
        set_name_num_to_prints = {
            ('SET', 'NAME', 'NUM'): ['printing', 'p2', 'p3']}

        card_dict = {
            'set': 'SET', 'name': 'NAME', 'number': 'NUM', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertEqual('printing', printing)

    def test_get_printing_set_name_num_mv_duplicate(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {
            ('SET', 'NAME', 'NUM', 'MV'): ['printing', 'p2']}
        set_name_mv_to_prints = {
            ('SET', 'NAME', 'MV'): ['printing', 'p2', 'p3']}
        set_name_num_to_prints = {
            ('SET', 'NAME', 'NUM'): ['printing', 'p2', 'p3']}

        card_dict = {
            'set': 'SET', 'name': 'NAME', 'number': 'NUM', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_none_set(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {(None, 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {(None, 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {(None, 'NAME', 'NUM'): ['printing']}

        card_dict = {'name': 'NAME', 'number': 'NUM', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_none_name(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', None, 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', None, 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', None, 'NUM'): ['printing']}

        card_dict = {'set': 'SET', 'number': 'NUM', 'multiverseid': 'MV'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertIsNone(printing)

    def test_get_printing_by_id(self):
        # Setup
        id_to_print = {'ID': 'printing'}
        set_name_num_mv_to_prints = {('SET', 'NAME', 'NUM', 'MV'): ['printing']}
        set_name_mv_to_prints = {('SET', 'NAME', 'MV'): ['printing']}
        set_name_num_to_prints = {('SET', 'NAME', 'NUM'): ['printing']}

        card_dict = {'id': 'ID'}

        # Execute
        printing = mtgdict.get_printing(
            card_dict, id_to_print, set_name_num_mv_to_prints,
            set_name_mv_to_prints, set_name_num_to_prints)

        # Verify
        self.assertEqual('printing', printing)

    def test_load_counts(self):
        # Setup
        mtgjson.update_models(self.session, self.mtg_data, False)
        self.session.commit()

        forest1 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2746).first()
        forest2 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2747).first()
        forest3 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2748).first()
        forest4 = self.session.query(
            models.CardPrinting).filter_by(multiverseid=2749).first()
        forest4.counts['copies'] = 2
        forest4.counts['foils'] = 3
        self.session.commit()
        # pylint: disable=line-too-long
        card_dicts = [
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2746, 'number': None, 'copies': 1},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2747, 'number': None, 'foils': 2},
            {'set': 'ICE', 'name': 'Forest', 'multiverseid': 2748, 'number': None, 'copies': 3, 'foils': 4},
            {'set': 'ICE', 'name': 'Snow-Covered Forest', 'multiverseid': 2749, 'number': None, 'copies': None, 'foils': None},
        ]
        # pylint: enable=line-too-long

        # Execute
        mtgdict.load_counts(self.session, card_dicts)
        self.session.commit()

        # Verify
        self.assertEqual({'copies': 1}, forest1.counts)
        self.assertEqual({'foils': 2}, forest2.counts)
        self.assertEqual({'copies': 3, 'foils': 4}, forest3.counts)
        self.assertFalse(forest4.counts)
