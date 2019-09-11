"""Tests for mtg_ssm.containers.indexes."""

from uuid import UUID

from mtg_ssm.containers.bundles import ScryfallDataSet
from mtg_ssm.containers.indexes import ScryfallDataIndex


def test_load_data(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)


def test_id_to_card(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)
    assert (
        index.id_to_card[UUID("59cf0906-04fa-4b30-a7a6-3d117931154f")].name
        == "Abattoir Ghoul"
    )


def test_name_to_cards(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)

    # set sorting
    assert [c.set for c in index.name_to_cards["Dark Ritual"]] == ["hop", "ice", "lea"]

    # collector number sorting
    assert [(c.set, c.collector_number) for c in index.name_to_cards["Forest"]] == [
        ("ice", "380"),
        ("ice", "381"),
        ("ice", "382"),
        ("isd", "262"),
        ("isd", "263"),
        ("isd", "264"),
        ("lea", "294"),
        ("lea", "295"),
    ]

    # collector number variant sorting
    assert [(c.set, c.collector_number) for c in index.name_to_cards["Thallid"]] == [
        ("fem", "74a"),
        ("fem", "74b"),
        ("fem", "74c"),
        ("fem", "74d"),
        ("mma", "167"),
    ]


def test_setcode_to_cards(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)

    # collector number sorting
    assert [(c.name, c.collector_number) for c in index.setcode_to_cards["isd"]] == [
        ("Delver of Secrets // Insectile Aberration", "51"),
        ("Abattoir Ghoul", "85"),
        ("Forest", "262"),
        ("Forest", "263"),
        ("Forest", "264"),
    ]

    # collector number variant sorting
    assert [c.collector_number for c in index.setcode_to_cards["fem"]] == [
        "74a",
        "74b",
        "74c",
        "74d",
    ]


def test_id_to_setindex(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)

    assert {
        c.id: index.id_to_setindex[c.id] for c in index.setcode_to_cards["isd"]
    } == {
        UUID("11bf83bb-c95b-4b4f-9a56-ce7a1816307a"): 0,
        UUID("59cf0906-04fa-4b30-a7a6-3d117931154f"): 1,
        UUID("b606f644-1728-4cb3-90ed-121838875de1"): 2,
        UUID("16f52885-1f01-4f06-90a8-1a0ecf291ab5"): 3,
        UUID("4dea3762-c6ae-4304-aee4-6c3f56685319"): 4,
    }


def test_setcode_to_set(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)

    assert index.setcode_to_set["isd"].name == "Innistrad"


def test_snnma_to_id(scryfall_data: ScryfallDataSet) -> None:
    index = ScryfallDataIndex()
    index.load_data(scryfall_data)

    assert {
        k
        for k, v in index.snnma_to_id.items()
        if v == {UUID("59cf0906-04fa-4b30-a7a6-3d117931154f")}
    } == {
        ("isd", "Abattoir Ghoul", "85", 222911, None),
        ("isd", "Abattoir Ghoul", "85", None, None),
        ("isd", "Abattoir Ghoul", None, 222911, None),
        ("isd", "Abattoir Ghoul", None, None, None),
        ("isd", "Abattoir Ghoul", "85", 222911, "Volkan Baǵa"),
        ("isd", "Abattoir Ghoul", "85", None, "Volkan Baǵa"),
        ("isd", "Abattoir Ghoul", None, 222911, "Volkan Baǵa"),
        ("isd", "Abattoir Ghoul", None, None, "Volkan Baǵa"),
        (None, "Abattoir Ghoul", "85", 222911, None),
        (None, "Abattoir Ghoul", "85", None, None),
        (None, "Abattoir Ghoul", None, 222911, None),
        (None, "Abattoir Ghoul", None, None, None),
        (None, "Abattoir Ghoul", "85", 222911, "Volkan Baǵa"),
        (None, "Abattoir Ghoul", "85", None, "Volkan Baǵa"),
        (None, "Abattoir Ghoul", None, 222911, "Volkan Baǵa"),
        (None, "Abattoir Ghoul", None, None, "Volkan Baǵa"),
    }

    assert {
        k
        for k, v in index.snnma_to_id.items()
        if v == {UUID("11bf83bb-c95b-4b4f-9a56-ce7a1816307a")}
    } == {
        ("isd", "Delver of Secrets // Insectile Aberration", "51", 226749, None),
        ("isd", "Delver of Secrets // Insectile Aberration", "51", 226755, None),
        ("isd", "Delver of Secrets // Insectile Aberration", "51", None, None),
        ("isd", "Delver of Secrets // Insectile Aberration", None, 226749, None),
        ("isd", "Delver of Secrets // Insectile Aberration", None, 226755, None),
        ("isd", "Delver of Secrets // Insectile Aberration", None, None, None),
        ("isd", "Delver of Secrets", "51", 226749, None),
        ("isd", "Delver of Secrets", "51", 226755, None),
        ("isd", "Delver of Secrets", "51", None, None),
        ("isd", "Delver of Secrets", "51a", 226749, None),
        ("isd", "Delver of Secrets", "51a", 226755, None),
        ("isd", "Delver of Secrets", "51a", None, None),
        ("isd", "Delver of Secrets", None, 226749, None),
        ("isd", "Delver of Secrets", None, 226755, None),
        ("isd", "Delver of Secrets", None, None, None),
        ("isd", "Insectile Aberration", "51", 226749, None),
        ("isd", "Insectile Aberration", "51", 226755, None),
        ("isd", "Insectile Aberration", "51", None, None),
        ("isd", "Insectile Aberration", "51b", 226749, None),
        ("isd", "Insectile Aberration", "51b", 226755, None),
        ("isd", "Insectile Aberration", "51b", None, None),
        ("isd", "Insectile Aberration", None, 226749, None),
        ("isd", "Insectile Aberration", None, 226755, None),
        ("isd", "Insectile Aberration", None, None, None),
        ("isd", "Delver of Secrets // Insectile Aberration", "51", 226749, "Nils Hamm"),
        ("isd", "Delver of Secrets // Insectile Aberration", "51", 226755, "Nils Hamm"),
        ("isd", "Delver of Secrets // Insectile Aberration", "51", None, "Nils Hamm"),
        ("isd", "Delver of Secrets // Insectile Aberration", None, 226749, "Nils Hamm"),
        ("isd", "Delver of Secrets // Insectile Aberration", None, 226755, "Nils Hamm"),
        ("isd", "Delver of Secrets // Insectile Aberration", None, None, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51", 226749, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51", 226755, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51", None, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51a", 226749, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51a", 226755, "Nils Hamm"),
        ("isd", "Delver of Secrets", "51a", None, "Nils Hamm"),
        ("isd", "Delver of Secrets", None, 226749, "Nils Hamm"),
        ("isd", "Delver of Secrets", None, 226755, "Nils Hamm"),
        ("isd", "Delver of Secrets", None, None, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51", 226749, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51", 226755, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51", None, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51b", 226749, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51b", 226755, "Nils Hamm"),
        ("isd", "Insectile Aberration", "51b", None, "Nils Hamm"),
        ("isd", "Insectile Aberration", None, 226749, "Nils Hamm"),
        ("isd", "Insectile Aberration", None, 226755, "Nils Hamm"),
        ("isd", "Insectile Aberration", None, None, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", "51", 226749, None),
        (None, "Delver of Secrets // Insectile Aberration", "51", 226755, None),
        (None, "Delver of Secrets // Insectile Aberration", "51", None, None),
        (None, "Delver of Secrets // Insectile Aberration", None, 226749, None),
        (None, "Delver of Secrets // Insectile Aberration", None, 226755, None),
        (None, "Delver of Secrets // Insectile Aberration", None, None, None),
        (None, "Delver of Secrets", "51", 226749, None),
        (None, "Delver of Secrets", "51", 226755, None),
        (None, "Delver of Secrets", "51", None, None),
        (None, "Delver of Secrets", "51a", 226749, None),
        (None, "Delver of Secrets", "51a", 226755, None),
        (None, "Delver of Secrets", "51a", None, None),
        (None, "Delver of Secrets", None, 226749, None),
        (None, "Delver of Secrets", None, 226755, None),
        (None, "Delver of Secrets", None, None, None),
        (None, "Insectile Aberration", "51", 226749, None),
        (None, "Insectile Aberration", "51", 226755, None),
        (None, "Insectile Aberration", "51", None, None),
        (None, "Insectile Aberration", "51b", 226749, None),
        (None, "Insectile Aberration", "51b", 226755, None),
        (None, "Insectile Aberration", "51b", None, None),
        (None, "Insectile Aberration", None, 226749, None),
        (None, "Insectile Aberration", None, 226755, None),
        (None, "Insectile Aberration", None, None, None),
        (None, "Delver of Secrets // Insectile Aberration", "51", 226749, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", "51", 226755, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", "51", None, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", None, 226749, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", None, 226755, "Nils Hamm"),
        (None, "Delver of Secrets // Insectile Aberration", None, None, "Nils Hamm"),
        (None, "Delver of Secrets", "51", 226749, "Nils Hamm"),
        (None, "Delver of Secrets", "51", 226755, "Nils Hamm"),
        (None, "Delver of Secrets", "51", None, "Nils Hamm"),
        (None, "Delver of Secrets", "51a", 226749, "Nils Hamm"),
        (None, "Delver of Secrets", "51a", 226755, "Nils Hamm"),
        (None, "Delver of Secrets", "51a", None, "Nils Hamm"),
        (None, "Delver of Secrets", None, 226749, "Nils Hamm"),
        (None, "Delver of Secrets", None, 226755, "Nils Hamm"),
        (None, "Delver of Secrets", None, None, "Nils Hamm"),
        (None, "Insectile Aberration", "51", 226749, "Nils Hamm"),
        (None, "Insectile Aberration", "51", 226755, "Nils Hamm"),
        (None, "Insectile Aberration", "51", None, "Nils Hamm"),
        (None, "Insectile Aberration", "51b", 226749, "Nils Hamm"),
        (None, "Insectile Aberration", "51b", 226755, "Nils Hamm"),
        (None, "Insectile Aberration", "51b", None, "Nils Hamm"),
        (None, "Insectile Aberration", None, 226749, "Nils Hamm"),
        (None, "Insectile Aberration", None, 226755, "Nils Hamm"),
        (None, "Insectile Aberration", None, None, "Nils Hamm"),
    }

    assert {
        k
        for k, v in index.snnma_to_id.items()
        if UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233") in v
    } == {
        ("fem", "Thallid", "74a", 1924, None),
        ("fem", "Thallid", "74a", None, None),
        ("fem", "Thallid", None, 1924, None),
        ("fem", "Thallid", None, None, None),
        ("fem", "Thallid", "74a", 1924, "Edward P. Beard, Jr."),
        ("fem", "Thallid", "74a", None, "Edward P. Beard, Jr."),
        ("fem", "Thallid", None, 1924, "Edward P. Beard, Jr."),
        ("fem", "Thallid", None, None, "Edward P. Beard, Jr."),
        (None, "Thallid", "74a", 1924, None),
        (None, "Thallid", "74a", None, None),
        (None, "Thallid", None, 1924, None),
        (None, "Thallid", None, None, None),
        (None, "Thallid", "74a", 1924, "Edward P. Beard, Jr."),
        (None, "Thallid", "74a", None, "Edward P. Beard, Jr."),
        (None, "Thallid", None, 1924, "Edward P. Beard, Jr."),
        (None, "Thallid", None, None, "Edward P. Beard, Jr."),
    }
    assert index.snnma_to_id[("fem", "Thallid", None, None, None)] == {
        UUID("4caaf31b-86a9-485b-8da7-d5b526ed1233"),
        UUID("80f8f778-ae31-45cd-b27f-f93a07853ede"),
        UUID("2cf2f3da-9101-439d-8caa-910ff40bfbb3"),
        UUID("01827286-b104-41c5-bac9-7c38414bc40e"),
    }
