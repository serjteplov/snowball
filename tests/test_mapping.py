"""Tests for the MTS name-to-symbol mapping."""

from __future__ import annotations

import logging

import pytest

from package_snowball.core.mapping import map_symbol


def test_map_symbol_known_stock() -> None:
    """A known stock name maps to its ticker."""
    assert map_symbol("ПАО Сбербанк, ап") == "SBER"


def test_map_symbol_known_bond() -> None:
    """A known bond name maps to its ISIN."""
    assert map_symbol('ОАО "Российские железные дороги", обл.') == "RU000A10C8C0"


def test_map_symbol_unknown_logs_and_raises(caplog: pytest.LogCaptureFixture) -> None:
    """An unknown name logs a warning and raises ValueError."""
    caplog.set_level(logging.WARNING)
    with pytest.raises(ValueError, match="Unknown security name"):
        map_symbol("ПАО Неизвестная Компания")
    assert "Unknown security name" in caplog.text
