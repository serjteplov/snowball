"""End-to-end golden-file test for the MTS to Snowball pipeline."""

from __future__ import annotations

from pathlib import Path

from package_snowball.adapters.mts_report_reader import MtsReportReader
from package_snowball.adapters.snowball_csv_writer import SnowballCsvWriter
from package_snowball.core.transformer import MtsToSnowballTransformer


def test_sample_report_matches_golden_csv(tmp_path: Path) -> None:
    """Run the full pipeline on the sample MTS report and verify CSV output."""
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "docs" / "examples" / "input" / "1388701_01012026-31012026.xlsx"
    expected_path = repo_root / "tests" / "fixtures" / "expected_snowball.csv"
    output_path = tmp_path / "out.csv"

    assert input_path.exists(), f"Sample input not found: {input_path}"
    assert expected_path.exists(), f"Golden file not found: {expected_path}"

    reader = MtsReportReader(input_path)
    deals, cash, balances = reader.read()

    transformer = MtsToSnowballTransformer()
    rows = transformer.transform_deals(deals)
    rows.extend(transformer.transform_cash_movements(cash, balances, deals))

    writer = SnowballCsvWriter()
    writer.write(rows, output_path)

    expected_lines = expected_path.read_text(encoding="utf-8").splitlines()
    actual_lines = output_path.read_text(encoding="utf-8").splitlines()

    assert len(actual_lines) == len(expected_lines), (
        f"Line count mismatch: expected {len(expected_lines)}, got {len(actual_lines)}"
    )

    for i, (expected, actual) in enumerate(zip(expected_lines, actual_lines, strict=True)):
        assert actual == expected, (
            f"Mismatch at line {i + 1}:\n  expected: {expected!r}\n  actual:   {actual!r}"
        )
