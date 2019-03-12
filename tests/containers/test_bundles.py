"""Tests for mtg_ssm.containers.bundles."""

from uuid import UUID

from mtg_ssm.containers import bundles


def test_remove_digital(scryfall_data: bundles.ScryfallDataSet) -> None:
    assert "vma" in {s.code for s in scryfall_data.sets}
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") in {
        c.id for c in scryfall_data.cards
    }
    digital_removed = bundles.remove_digital(scryfall_data)
    assert "vma" not in {s.code for s in digital_removed.sets}
    assert UUID("116ec16c-3b4b-45be-83c8-333bccc29e35") not in {
        c.id for c in digital_removed.cards
    }
