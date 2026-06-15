# Progress

Project bootstrapped with Python 3.13+, `src/` layout, pytest, ruff, mypy, pre-commit.

## 2026-06-14 — Design & Spec

- Interviewed requirements, explored MTS `.xlsx` sample and Snowball CSV template.
- Selected ETL pipeline with domain models (inside-out implementation).
- Wrote spec `docs/specs/2026-06-15-mts-transformer.md` and ADR `0002-mts-to-snowball-transformer-architecture.md`.

## 2026-06-15 — Implementation complete

- `core/models.py` — `SnowballRow`, `DealCompletedRow`, `CashMovementRow`, `SecurityBalanceRow`
- `core/mapping.py` — hard-coded `MTS_NAME_TO_TICKER` with deterministic suffix stripping
- `core/transformer.py` — `MtsToSnowballTransformer` with fail-fast error handling and logging
- `adapters/mts_report_reader.py` — `openpyxl`-based reader for MTS report sections
- `adapters/snowball_csv_writer.py` — stdlib `csv` writer with UTF-8 BOM and safe Decimal formatting
- `entrypoints/cli.py` — `transform-mts` subcommand
- Tests: 33 unit tests covering mapping, transformer, reader, writer, and smoke
- `make check` clean

## Next step

- Await user review or start the next prioritized task (e.g., API to transform brokerage reports online).
