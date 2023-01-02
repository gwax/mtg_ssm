"""Tests for mtg_ssm.containers.bundles."""

from uuid import UUID

from mtg_ssm.containers import bundles
from mtg_ssm.scryfall.models import ScryCardLayout


def test_remove_digital(scryfall_data: bundles.ScryfallDataSet) -> None:
    set_codes = {s.code for s in scryfall_data.sets}
    card_ids = {c.id for c in scryfall_data.cards}
    card_names = {c.name for c in scryfall_data.cards}

    assert "vma" in set_codes
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") in card_ids

    assert "khm" in set_codes
    assert "Cosmos Elixir" in card_names
    assert "A-Cosmos Elixir" in card_names

    digital_removed = bundles.filter_cards_and_sets(scryfall_data, exclude_digital=True)
    set_codes2 = {s.code for s in digital_removed.sets}
    card_ids2 = {c.id for c in digital_removed.cards}
    card_names2 = {c.name for c in digital_removed.cards}

    assert "vma" not in set_codes2
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") not in card_ids2

    assert "khm" in set_codes2
    assert "Cosmos Elixir" in card_names2
    assert "A-Cosmos Elixir" not in card_names2


def test_exclude_token_layout(scryfall_data: bundles.ScryfallDataSet) -> None:
    set_codes = {s.code for s in scryfall_data.sets}
    card_names = {c.name for c in scryfall_data.cards}

    assert "p03" in set_codes and "sld" in set_codes
    assert "Goblin" in card_names

    tokens_removed = bundles.filter_cards_and_sets(
        scryfall_data, exclude_card_layouts={ScryCardLayout.TOKEN}
    )
    set_codes2 = {s.code for s in tokens_removed.sets}
    card_names2 = {c.name for c in tokens_removed.cards}
    assert "p03" not in set_codes2 and "sld" in set_codes2
    assert "Goblin" not in card_names2


def test_exclude_foreign_only(scryfall_data: bundles.ScryfallDataSet) -> None:
    set_codes = {s.code for s in scryfall_data.sets}
    card_ids = {c.id for c in scryfall_data.cards}

    assert "ren" in set_codes
    assert UUID("81917a2b-9bf6-4aa6-947d-36b0f45d6fe3") in card_ids

    tokens_removed = bundles.filter_cards_and_sets(
        scryfall_data, exclude_foreing_only=True
    )
    set_codes2 = {s.code for s in tokens_removed.sets}
    card_ids2 = {c.id for c in tokens_removed.cards}
    assert "ren" not in set_codes2
    assert UUID("81917a2b-9bf6-4aa6-947d-36b0f45d6fe3") not in card_ids2
