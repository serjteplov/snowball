"""Write Snowball-compatible CSV files."""

from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from package_snowball.core.models import SnowballRow

_SNOWBALL_HEADER = [
    "Event",
    "Date",
    "Symbol",
    "Price",
    "Quantity",
    "Currency",
    "FeeTax",
    "Exchange",
    "NKD",
    "FeeCurrency",
    "DoNotAdjustCash",
    "Note",
]


def _format_field(value: object) -> str:
    """Format a single field for CSV output."""
    if isinstance(value, Decimal):
        # Use fixed-point notation to avoid scientific notation.
        return format(value, "f")
    if isinstance(value, bool):
        return "True" if value else ""
    return str(value) if value is not None else ""


class SnowballCsvWriter:
    """Write a list of SnowballRow objects to a CSV file."""

    def write(self, rows: list[SnowballRow], path: Path) -> None:
        """Write rows to path with UTF-8 BOM for Excel compatibility."""
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(_SNOWBALL_HEADER)
            for row in rows:
                writer.writerow(
                    [
                        row.event,
                        row.date.isoformat(),
                        row.symbol,
                        _format_field(row.price),
                        _format_field(row.quantity),
                        row.currency,
                        _format_field(row.fee_tax),
                        row.exchange,
                        _format_field(row.nkd),
                        row.fee_currency,
                        _format_field(row.do_not_adjust_cash),
                        row.note,
                    ]
                )
