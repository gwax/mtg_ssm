"""Tests for mtg_ssm.mtg.counts"""
# pylint: disable=redefined-outer-name

import pytest

from mtg_ssm.mtg import card_db
from mtg_ssm.mtg import counts

TEST_PRINT_ID = "958ae1416f8f6287115ccd7c5c61f2415a313546"


@pytest.fixture(scope="module")
def cdb(sets_data):
    """Fixture card_db with mtg json data."""
    return card_db.CardDb(sets_data)


@pytest.mark.parametrize(
    "raw_card_row,expected_card_row",
    [
        ({}, {}),
        ({"multiverseid": "17"}, {"multiverseid": 17}),
        ({"copies": "4"}, {"copies": 4}),
        ({"foils": "7"}, {"foils": 7}),
        ({"multiverseid": "a"}, {"multiverseid": "a"}),
        ({"copies": "b"}, {"copies": "b"}),
        ({"foils": "c"}, {"foils": "c"}),
        (
            {"id": "a", "multiverseid": "12", "copies": "4", "foils": "5"},
            {"id": "a", "multiverseid": 12, "copies": 4, "foils": 5},
        ),
    ],
)
def test_coerce_card_row(raw_card_row, expected_card_row):
    assert counts.coerce_card_row(raw_card_row) == expected_card_row


@pytest.mark.parametrize(
    "card_rows,strict,expected",
    [
        ([], True, {}),
        ([{}], True, {}),
        ([{"copies": 0}], True, {}),
        pytest.mark.xfail(
            ([{"copies": 1}], True, "N/A"), raises=counts.UnknownPrintingError
        ),
        ([{"id": TEST_PRINT_ID}], True, {}),
        ([{"id": TEST_PRINT_ID, "copies": 0, "foils": 0}], True, {}),
        (
            [{"id": TEST_PRINT_ID, "copies": 1, "foils": 2}],
            True,
            {TEST_PRINT_ID: {counts.CountTypes.copies: 1, counts.CountTypes.foils: 2}},
        ),
        (
            [{"set": "S00", "name": "Rhox", "copies": 1}],
            True,
            {"536d407161fa03eddee7da0e823c2042a8fa0262": {counts.CountTypes.copies: 1}},
        ),
        (
            [
                {"id": TEST_PRINT_ID, "copies": 1, "foils": 2},
                {"set": "S00", "name": "Rhox", "copies": 1},
            ],
            True,
            {
                TEST_PRINT_ID: {
                    counts.CountTypes.copies: 1,
                    counts.CountTypes.foils: 2,
                },
                "536d407161fa03eddee7da0e823c2042a8fa0262": {
                    counts.CountTypes.copies: 1
                },
            },
        ),
        (
            [
                {"id": TEST_PRINT_ID, "copies": 4},
                {"id": TEST_PRINT_ID, "copies": 3, "foils": "8"},
            ],
            True,
            {TEST_PRINT_ID: {counts.CountTypes.copies: 7, counts.CountTypes.foils: 8}},
        ),
        (
            [{"set": "LEA", "name": "Forest", "copies": 1}],
            False,
            {"5ede9781b0c5d157c28a15c3153a455d7d6180fa": {counts.CountTypes.copies: 1}},
        ),
        pytest.mark.xfail(
            (
                [{"set": "LEA", "name": "Forest", "copies": 1}],
                True,
                {
                    "5ede9781b0c5d157c28a15c3153a455d7d6180fa": {
                        counts.CountTypes.copies: 1
                    }
                },
            ),
            raises=counts.UnknownPrintingError,
        ),
    ],
)
def test_aggregate_print_counts(cdb, card_rows, strict, expected):
    print_counts = counts.aggregate_print_counts(cdb, card_rows, strict)
    assert print_counts == expected


@pytest.mark.parametrize(
    "in_print_counts,out_print_counts",
    [
        ([], {}),
        ([{"a": {"b": 2}}], {"a": {"b": 2}}),
        ([{"a": {"b": 2}}, {"a": {"b": 1, "c": 4}}], {"a": {"b": 3, "c": 4}}),
        (
            [{"a": {"b": 2}}, {"a": {"c": 1}, "b": {"c": 3}}, {"a": {"c": 5}}],
            {"a": {"b": 2, "c": 6}, "b": {"c": 3}},
        ),
    ],
)
def test_merge_print_counts(in_print_counts, out_print_counts):
    assert counts.merge_print_counts(*in_print_counts) == out_print_counts


@pytest.mark.parametrize(
    "left,right,output",
    [
        ({}, {}, {}),
        ({"a": {"b": 2}}, {"a": {"b": 1}}, {"a": {"b": 1}}),
        ({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": -1}}),
        ({"a": {"b": 1}}, {"a": {"b": 1}}, {}),
        ({"a": {"b": 1}}, {"c": {"d": 1}}, {"a": {"b": 1}, "c": {"d": -1}}),
    ],
)
def test_diff_ptin_counts(left, right, output):
    assert counts.diff_print_counts(left, right) == output


# Printing lookup tests
@pytest.mark.parametrize(
    "set_code,name,set_number,multiverseid",
    [
        ("foo", "bar", "baz", "quux"),  # not matching printing
        ("ICE", "Forest", None, None),  # multiple matches
        ("foo", "Abattoir Ghoul", "85", 222911),  # bad set_code
        ("ISD", "foo", "85", 222911),  # bad name
    ],
)
def test_printing_not_found(cdb, set_code, name, set_number, multiverseid):
    printing = counts.find_printing(
        cdb=cdb,
        set_code=set_code,
        name=name,
        set_number=set_number,
        multiverseid=multiverseid,
    )
    assert printing is None


@pytest.mark.parametrize(
    "set_code,name,set_number,multiverseid,found_id",
    [
        # pylint: disable=line-too-long
        ("S00", "Rhox", "foo", "bar", "536d407161fa03eddee7da0e823c2042a8fa0262"),
        (
            "pMGD",
            "Black Sun's Zenith",
            "7",
            "foo",
            "6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc",
        ),
        ("LEA", "Forest", "foo", 288, "5ede9781b0c5d157c28a15c3153a455d7d6180fa"),
        (
            "ISD",
            "Abattoir Ghoul",
            "85",
            222911,
            "958ae1416f8f6287115ccd7c5c61f2415a313546",
        ),
        (
            "PC2",
            "Chaotic Æther",
            "foo",
            "bar",
            "c98cdec5d2201abe3411db460cb088b82945bb9e",
        ),
        (
            "PC2",
            "Chaotic Aether",
            "foo",
            "bar",
            "c98cdec5d2201abe3411db460cb088b82945bb9e",
        ),
        (
            "CSP",
            "Jötun Grunt",
            "foo",
            "bar",
            "b6d3b800eee5851e4727adf50d9c2d82f269f25f",
        ),
        (
            "CSP",
            "Jotun Grunt",
            "foo",
            "bar",
            "b6d3b800eee5851e4727adf50d9c2d82f269f25f",
        ),
    ],
)
def test_found_printing(cdb, set_code, name, set_number, multiverseid, found_id):
    printing = counts.find_printing(
        cdb=cdb,
        set_code=set_code,
        name=name,
        set_number=set_number,
        multiverseid=multiverseid,
    )
    assert printing.id_ == found_id
