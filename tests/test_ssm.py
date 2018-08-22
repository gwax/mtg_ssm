"""Tests for mtg_ssm.manager module."""

import argparse as ap
import os
import tempfile
import textwrap

import freezegun
import pytest

from mtg_ssm import ssm
from mtg_ssm.mtg import card_db


@pytest.fixture
def cdb(sets_data):
    """card_db fixture for testing."""
    sets_data = {k: v for k, v in sets_data.items() if k in {"MMA", "pMGD"}}
    return card_db.CardDb(sets_data)


@pytest.fixture(autouse=True)
def patch_build_card_db(monkeypatch, cdb):
    """Fixture to monkeypatch build_card_db for testing."""

    def mock_build_cdb(*_):
        """Build card_db method that always returns fixed value."""
        return cdb

    monkeypatch.setattr(ssm, "build_card_db", mock_build_cdb)


def get_namespace(**kwargs):
    """Namespace with defaults constructor."""
    defaults = {
        "data_path": ssm.DEFAULT_DATA_PATH,
        "include_online_only": False,
        "dialect": {},
    }
    defaults.update(kwargs)
    return ap.Namespace(**defaults)


@pytest.mark.parametrize(
    "cmdline,expected",
    [
        (
            "create testfilename",
            get_namespace(
                action="create", func=ssm.create_cmd, collection="testfilename"
            ),
        ),
        (
            "update testfilename",
            get_namespace(
                action="update", func=ssm.update_cmd, collection="testfilename"
            ),
        ),
        (
            "merge testfilename otherfile1",
            get_namespace(
                action="merge",
                func=ssm.merge_cmd,
                collection="testfilename",
                imports=["otherfile1"],
            ),
        ),
        (
            "merge testfilename otherfile1 otherfile2 otherfile3",
            get_namespace(
                action="merge",
                func=ssm.merge_cmd,
                collection="testfilename",
                imports=["otherfile1", "otherfile2", "otherfile3"],
            ),
        ),
        (
            "diff file1 file2 file3",
            get_namespace(
                action="diff",
                func=ssm.diff_cmd,
                output="file3",
                left="file1",
                right="file2",
            ),
        ),
        (
            "--data-path /foo --include-online-only " "create testfilename",
            get_namespace(
                data_path="/foo",
                include_online_only=True,
                action="create",
                func=ssm.create_cmd,
                collection="testfilename",
            ),
        ),
        (
            "--dialect foo bar --dialect baz quux " "create testfilename",
            get_namespace(
                data_path=ssm.DEFAULT_DATA_PATH,
                include_online_only=False,
                dialect={"foo": "bar", "baz": "quux"},
                action="create",
                func=ssm.create_cmd,
                collection="testfilename",
            ),
        ),
    ],
)
def test_get_args(cmdline, expected):
    args = ssm.get_args(args=cmdline.split())
    assert args == expected


def test_create_cmd():
    with tempfile.NamedTemporaryFile(mode="rt", suffix=".csv") as outfile:
        args = get_namespace(
            action="create", func=ssm.create_cmd, collection=outfile.name
        )
        ssm.create_cmd(args)
        outdata = outfile.read()
    assert outdata == textwrap.dedent(
        """\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,,
        """
    )


@freezegun.freeze_time("2015-06-28 01:02:03")
def test_update_cmd():
    with tempfile.TemporaryDirectory() as tmpdirname:
        infilename = os.path.join(tmpdirname, "infile.csv")
        with open(infilename, "wt") as infile:
            infile.write(
                textwrap.dedent(
                    """\
                    id,copies,foils
                    fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
                    """
                )
            )
        args = get_namespace(
            action="update", func=ssm.update_cmd, collection=infilename
        )
        ssm.update_cmd(args)
        assert set(os.listdir(tmpdirname)) == {
            "infile.csv",
            "infile.20150628_010203.csv",
        }
        with open(infilename, "rt") as outfile:
            outfiledata = outfile.read()
        bakfilename = os.path.join(tmpdirname, "infile.20150628_010203.csv")
        with open(bakfilename) as bakfile:
            bakfiledata = bakfile.read()
    assert outfiledata == textwrap.dedent(
        """\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )
    assert bakfiledata == textwrap.dedent(
        """\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )


def test_merge_cmd_new():
    with tempfile.TemporaryDirectory() as tmpdirname:
        outfilename = os.path.join(tmpdirname, "outfile.csv")
        importname = os.path.join(tmpdirname, "import.csv")
        with open(importname, "wt") as infile:
            infile.write(
                textwrap.dedent(
                    """\
                    id,copies,foils
                    fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
                    """
                )
            )
        args = get_namespace(
            action="merge",
            func=ssm.merge_cmd,
            collection=outfilename,
            imports=[importname],
        )
        ssm.merge_cmd(args)
        assert set(os.listdir(tmpdirname)) == {"import.csv", "outfile.csv"}
        with open(outfilename, "rt") as outfile:
            outfiledata = outfile.read()
        with open(importname, "rt") as importfile:
            importdata = importfile.read()
    assert outfiledata == textwrap.dedent(
        """\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )
    assert importdata == textwrap.dedent(
        """\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )


@freezegun.freeze_time("2015-06-28 04:05:06")
def test_merge_cmd_existing():
    with tempfile.TemporaryDirectory() as tmpdirname:
        outfilename = os.path.join(tmpdirname, "outfile.csv")
        importname = os.path.join(tmpdirname, "import.csv")
        for filename in [outfilename, importname]:
            with open(filename, "wt") as infile:
                infile.write(
                    textwrap.dedent(
                        """\
                        id,copies,foils
                        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
                        """
                    )
                )
        args = get_namespace(
            action="merge",
            func=ssm.merge_cmd,
            collection=outfilename,
            imports=[importname],
        )
        ssm.merge_cmd(args)
        assert set(os.listdir(tmpdirname)) == {
            "import.csv",
            "outfile.csv",
            "outfile.20150628_040506.csv",
        }
        with open(outfilename, "rt") as outfile:
            outfiledata = outfile.read()
        with open(importname, "rt") as importfile:
            importdata = importfile.read()
        bakfilename = os.path.join(tmpdirname, "outfile.20150628_040506.csv")
        with open(bakfilename) as bakfile:
            bakfiledata = bakfile.read()
    assert outfiledata == textwrap.dedent(
        """\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,8,16
        """
    )
    assert importdata == textwrap.dedent(
        """\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )
    assert bakfiledata == textwrap.dedent(
        """\
        id,copies,foils
        fc46a4b72d216117a352f59217a84d0baeaaacb7,4,8
        """
    )


def test_diff_cmd():
    with tempfile.TemporaryDirectory() as tmpdirname:
        leftfilename = os.path.join(tmpdirname, "left.csv")
        rightfilename = os.path.join(tmpdirname, "right.csv")
        outfilename = os.path.join(tmpdirname, "out.csv")
        with open(leftfilename, "wt") as leftfile:
            leftfile.write(
                textwrap.dedent(
                    """\
                    id,copies,foils
                    fc46a4b72d216117a352f59217a84d0baeaaacb7,2,
                    """
                )
            )
        with open(rightfilename, "wt") as rightfile:
            rightfile.write(
                textwrap.dedent(
                    """\
                    id,copies,foils
                    6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,4,
                    fc46a4b72d216117a352f59217a84d0baeaaacb7,1,3
                    """
                )
            )
        args = get_namespace(
            action="diff",
            func=ssm.diff_cmd,
            output=outfilename,
            left=leftfilename,
            right=rightfilename,
        )
        ssm.diff_cmd(args)
        assert set(os.listdir(tmpdirname)) == {"left.csv", "right.csv", "out.csv"}
        with open(outfilename, "rt") as outfile:
            outfiledata = outfile.read()
    assert outfiledata == textwrap.dedent(
        """\
        set,name,number,multiverseid,id,copies,foils
        pMGD,Black Sun's Zenith,7,,6c9ffa9ffd2cf7e6f85c6be1713ee0c546b9f8fc,-4,
        MMA,Thallid,167,370352,fc46a4b72d216117a352f59217a84d0baeaaacb7,1,-3
        """
    )
