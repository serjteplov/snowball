"""CLI entrypoint for the MTS to Snowball transformer."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from package_snowball.adapters.mts_report_reader import MtsReportReader
from package_snowball.adapters.snowball_csv_writer import SnowballCsvWriter
from package_snowball.core.transformer import MtsToSnowballTransformer


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def transform_mts(input_path: Path, output_path: Path) -> None:
    """Transform an MTS report into a Snowball CSV."""
    reader = MtsReportReader(input_path)
    deals, cash, balances = reader.read()

    transformer = MtsToSnowballTransformer()
    snowball_rows = transformer.transform_deals(deals)
    snowball_rows.extend(transformer.transform_cash_movements(cash, balances, deals))

    writer = SnowballCsvWriter()
    writer.write(snowball_rows, output_path)


def main(argv: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    _setup_logging()
    parser = argparse.ArgumentParser(
        description="Convert brokerage reports to Snowball CSV",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    mts_parser = subparsers.add_parser(
        "transform-mts",
        help="Convert an MTS brokerage report to Snowball CSV",
    )
    mts_parser.add_argument("input", type=Path, help="Path to MTS .xlsx report")
    mts_parser.add_argument("output", type=Path, help="Path to output .csv file")

    args = parser.parse_args(argv)

    try:
        transform_mts(args.input, args.output)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Written {args.output}")
    return 0
