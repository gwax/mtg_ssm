"""Tests for mtg_ssm.containers.bundles."""

from uuid import UUID

from mtg_ssm.containers import bundles


def test_remove_digital(scryfall_data: bundles.ScryfallDataSet) -> None:
    set_codes = {s.code for s in scryfall_data.sets}
    card_ids = {c.id for c in scryfall_data.cards}
    card_names = {c.name for c in scryfall_data.cards}

    assert "vma" in set_codes
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") in card_ids

    assert "khm" in set_codes
    assert "Cosmos Elixir" in card_names
    assert "A-Cosmos Elixir" in card_names

    digital_removed = bundles.remove_digital(scryfall_data)
    set_codes2 = {s.code for s in digital_removed.sets}
    card_ids2 = {c.id for c in digital_removed.cards}
    card_names2 = {c.name for c in digital_removed.cards}

    assert "vma" not in set_codes2
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") not in card_ids2

    assert "khm" in set_codes2
    assert "Cosmos Elixir" in card_names2
    assert "A-Cosmos Elixir" not in card_names2
