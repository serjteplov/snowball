"""Tests for the Snowball CSV writer."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from package_snowball.adapters.snowball_csv_writer import SnowballCsvWriter
from package_snowball.core.models import SnowballRow


def test_writer_emits_header_and_rows(tmp_path: Path) -> None:
    writer = SnowballCsvWriter()
    path = tmp_path / "out.csv"
    rows = [
        SnowballRow(
            event="Buy",
            date=date(2026, 1, 13),
            symbol="LKOH",
            price=Decimal("5404"),
            quantity=Decimal("3"),
            currency="RUB",
            fee_tax=Decimal("6.49"),
            exchange="MCX",
            nkd=Decimal("0"),
            fee_currency="",
            do_not_adjust_cash=False,
            note="15222648488",
        ),
        SnowballRow(
            event="Cash_In",
            date=date(2026, 1, 13),
            symbol="RUB",
            price=Decimal("1"),
            quantity=Decimal("58000"),
            currency="RUB",
            fee_tax=Decimal("0"),
        ),
    ]
    writer.write(rows, path)

    content = path.read_text(encoding="utf-8")
    assert content.startswith("﻿")
    lines = content.strip().split("\n")
    assert len(lines) == 3
    expected_header = (
        "Event,Date,Symbol,Price,Quantity,Currency,FeeTax,"
        "Exchange,NKD,FeeCurrency,DoNotAdjustCash,Note"
    )
    assert lines[0].lstrip("﻿") == expected_header
    assert lines[1] == "Buy,2026-01-13,LKOH,5404,3,RUB,6.49,MCX,0,,,15222648488"
    assert lines[2] == "Cash_In,2026-01-13,RUB,1,58000,RUB,0,,0,,,"


def test_decimal_formatting_no_scientific_notation(tmp_path: Path) -> None:
    writer = SnowballCsvWriter()
    path = tmp_path / "out.csv"
    rows = [
        SnowballRow(
            event="Buy",
            date=date(2026, 1, 13),
            symbol="X",
            price=Decimal("0.00000123"),
            quantity=Decimal("1"),
            currency="RUB",
            fee_tax=Decimal("0"),
        ),
    ]
    writer.write(rows, path)
    content = path.read_text(encoding="utf-8")
    assert "1.23E-6" not in content
    assert "0.00000123" in content


def test_writer_empty_rows_emits_header_only(tmp_path: Path) -> None:
    writer = SnowballCsvWriter()
    path = tmp_path / "out.csv"
    writer.write([], path)
    content = path.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    assert len(lines) == 1
    assert lines[0].lstrip("﻿").startswith("Event,Date")


def test_writer_note_with_commas_is_quoted(tmp_path: Path) -> None:
    writer = SnowballCsvWriter()
    path = tmp_path / "out.csv"
    rows = [
        SnowballRow(
            event="Dividend",
            date=date(2026, 1, 13),
            symbol="TCSG",
            price=Decimal("36"),
            quantity=Decimal("108"),
            currency="RUB",
            fee_tax=Decimal("14"),
            note="Note with, commas",
        ),
    ]
    writer.write(rows, path)
    content = path.read_text(encoding="utf-8")
    assert '"Note with, commas"' in content
