"""Tests for mtg_ssm.manager module."""
# pylint: disable=redefined-outer-name

import argparse as ap
import textwrap
from pathlib import Path

import freezegun
import pytest
from _pytest.monkeypatch import MonkeyPatch

import mtg_ssm.scryfall.fetcher
from mtg_ssm import ssm
from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.indexes import Oracle
from mtg_ssm.scryfall.models import ScryCardLayout, ScrySetType


@pytest.fixture(scope="session")
def oracle(scryfall_data: ScryfallDataSet) -> Oracle:
    """Fixture for Oracle over only MMA and PMBS"""
    accepted_sets = {"mma", "pmbs"}
    scryfall_data2 = ScryfallDataSet(
        sets=[s for s in scryfall_data.sets if s.code in accepted_sets],
        cards=[c for c in scryfall_data.cards if c.set in accepted_sets],
        migrations=[],
    )
    return Oracle(scryfall_data2)


@pytest.fixture(autouse=True)
def patch_scryfetch(monkeypatch: MonkeyPatch, oracle: Oracle) -> None:
    """Fixture to monkeypatch build_card_db for testing."""

    def mock_scryfetch() -> Oracle:
        """Build card_db method that always returns fixed value."""
        return oracle

    monkeypatch.setattr(mtg_ssm.scryfall.fetcher, "scryfetch", mock_scryfetch)


@pytest.mark.parametrize(
    "cmdline, expected",
    [
        (
            "create testfilename",
            ap.Namespace(
                action="create",
                func=ssm.create_cmd,
                collection=Path("testfilename"),
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "--include-digital create testfilename",
            ap.Namespace(
                action="create",
                func=ssm.create_cmd,
                collection=Path("testfilename"),
                dialect={},
                include_digital=True,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "--dialect csv terse create testfilename",
            ap.Namespace(
                action="create",
                func=ssm.create_cmd,
                collection=Path("testfilename"),
                dialect={"csv": "terse"},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "--exclude-set-types=token,memorabilia,vanguard create testfilename",
            ap.Namespace(
                action="create",
                func=ssm.create_cmd,
                collection=Path("testfilename"),
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={
                    ScrySetType.TOKEN,
                    ScrySetType.MEMORABILIA,
                    ScrySetType.VANGUARD,
                },
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "update testfilename",
            ap.Namespace(
                action="update",
                func=ssm.update_cmd,
                collection=Path("testfilename"),
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "merge testfilename otherfile1",
            ap.Namespace(
                action="merge",
                func=ssm.merge_cmd,
                collection=Path("testfilename"),
                imports=[Path("otherfile1")],
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "merge testfilename otherfile1 otherfile2 otherfile3",
            ap.Namespace(
                action="merge",
                func=ssm.merge_cmd,
                collection=Path("testfilename"),
                imports=[Path("otherfile1"), Path("otherfile2"), Path("otherfile3")],
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
        (
            "diff file1 file2 file3",
            ap.Namespace(
                action="diff",
                func=ssm.diff_cmd,
                output=Path("file3"),
                left=Path("file1"),
                right=Path("file2"),
                dialect={},
                include_digital=False,
                include_foreign_only=False,
                separate_promos=False,
                exclude_set_types={ScrySetType.TOKEN, ScrySetType.MEMORABILIA},
                exclude_card_layouts={
                    ScryCardLayout.ART_SERIES,
                    ScryCardLayout.DOUBLE_FACED_TOKEN,
                    ScryCardLayout.EMBLEM,
                    ScryCardLayout.TOKEN,
                },
            ),
        ),
    ],
)
def test_get_args(cmdline: str, expected: ap.Namespace) -> None:
    assert ssm.get_args(args=cmdline.split()) == expected


def test_create_cmd(tmp_path: Path, oracle: Oracle) -> None:
    coll_path = tmp_path / "collection.csv"

    args = ap.Namespace(collection=coll_path, dialect={})
    ssm.create_cmd(args, oracle)

    assert coll_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,,
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,,
        """
    )


@freezegun.freeze_time("2015-06-28 01:02:03")
def test_update_cmd(tmp_path: Path, oracle: Oracle) -> None:
    work_path = tmp_path / "work"
    work_path.mkdir()
    coll_path = work_path / "collection.csv"
    expected_backup_path = work_path / "collection.20150628_010203.csv"

    coll_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
            """
        )
    )

    args = ap.Namespace(collection=coll_path, dialect={})
    ssm.update_cmd(args, oracle)

    assert set(work_path.iterdir()) == {coll_path, expected_backup_path}
    assert coll_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,,
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
        """
    )
    assert expected_backup_path.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
        """
    )


def test_merge_cmd_new(tmp_path: Path, oracle: Oracle) -> None:
    work_path = tmp_path / "work"
    work_path.mkdir()
    coll_path = work_path / "collection.csv"
    import_path = work_path / "import.csv"

    import_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
            """
        )
    )

    args = ap.Namespace(collection=coll_path, imports=[import_path], dialect={})
    ssm.merge_cmd(args, oracle)

    assert set(work_path.iterdir()) == {coll_path, import_path}
    assert coll_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,,
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
        """
    )
    assert import_path.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,4,9
        """
    )


@freezegun.freeze_time("2015-06-28 04:05:06")
def test_merge_cmd_existing(tmp_path: Path, oracle: Oracle) -> None:
    work_path = tmp_path / "work"
    work_path.mkdir()
    coll_path = work_path / "collection.csv"
    import_path = work_path / "import.csv"
    expected_backup_path = work_path / "collection.20150628_040506.csv"

    coll_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,1,3
            """
        )
    )
    import_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,5,7
            """
        )
    )

    args = ap.Namespace(collection=coll_path, imports=[import_path], dialect={})
    ssm.merge_cmd(args, oracle)

    assert set(work_path.iterdir()) == {coll_path, import_path, expected_backup_path}
    assert coll_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,,
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,6,10
        """
    )
    assert import_path.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,5,7
        """
    )
    assert expected_backup_path.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,1,3
        """
    )


@freezegun.freeze_time("2015-06-28 08:09:10")
def test_merge_cmd_multiple(tmp_path: Path, oracle: Oracle) -> None:
    work_path = tmp_path / "work"
    work_path.mkdir()
    coll_path = work_path / "collection.csv"
    import_path1 = work_path / "import1.csv"
    import_path2 = work_path / "import2.csv"
    expected_backup_path = work_path / "collection.20150628_080910.csv"

    coll_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,1,3
            """
        )
    )
    import_path1.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,5,7
            """
        )
    )
    import_path2.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            dd88131a-2811-4a1f-bb9a-c82e12c1493b,19,23
            """
        )
    )

    args = ap.Namespace(
        collection=coll_path, imports=[import_path1, import_path2], dialect={}
    )
    ssm.merge_cmd(args, oracle)

    assert set(work_path.iterdir()) == {
        coll_path,
        import_path1,
        import_path2,
        expected_backup_path,
    }
    assert coll_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,19,23
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,6,10
        """
    )
    assert import_path1.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,5,7
        """
    )
    assert import_path2.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        dd88131a-2811-4a1f-bb9a-c82e12c1493b,19,23
        """
    )
    assert expected_backup_path.read_text() == textwrap.dedent(
        """\
        scryfall_id,nonfoil,foil
        69d20d28-76e9-4e6e-95c3-f88c51dfabfd,1,3
        """
    )


def test_diff_cmd(tmp_path: Path, oracle: Oracle) -> None:
    work_path = tmp_path / "work"
    work_path.mkdir()
    left_path = work_path / "left.csv"
    right_path = work_path / "right.csv"
    out_path = work_path / "out.csv"

    left_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,8,
            """
        )
    )
    right_path.write_text(
        textwrap.dedent(
            """\
            scryfall_id,nonfoil,foil
            dd88131a-2811-4a1f-bb9a-c82e12c1493b,4,
            69d20d28-76e9-4e6e-95c3-f88c51dfabfd,1,3
            """
        )
    )

    args = ap.Namespace(output=out_path, left=left_path, right=right_path, dialect={})
    ssm.diff_cmd(args, oracle)
    assert set(work_path.iterdir()) == {left_path, right_path, out_path}
    assert out_path.read_text() == textwrap.dedent(
        """\
        set,name,collector_number,scryfall_id,nonfoil,foil
        PMBS,Hero of Bladehold,8★,8829efa0-498a-43ca-91aa-f9caeeafe298,,
        PMBS,Black Sun's Zenith,39,dd88131a-2811-4a1f-bb9a-c82e12c1493b,-4,
        MMA,Thallid,167,69d20d28-76e9-4e6e-95c3-f88c51dfabfd,7,-3
        """
    )
