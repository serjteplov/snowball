# ADR-0002: MTS to Snowball Transformer Architecture

## Status
Accepted

## Context
We need to convert MTS brokerage reports (single-sheet `.xlsx`) into Snowball-compatible CSV. The MTS format is irregular: multiple sections (deals completed, cash movement, securities movement), Russian free-text descriptions, and no standard API. We evaluated three implementation approaches and made several structural choices.

## Decisions

### 1. ETL pipeline with domain models
We will use a layered **Extract → Transform → Load** pipeline rather than a monolithic script or plugin registry.

- **Extractor** (`adapters/mts_report_reader.py`) reads raw rows from the `.xlsx`.
- **Transformer** (`core/transformer.py`) applies business rules and mapping.
- **Writer** (`adapters/snowball_csv_writer.py`) emits the final CSV.

**Rationale:**
- Aligns with the existing repo structure (`core/`, `adapters/`, `entrypoints/`).
- Transformer is pure logic and trivial to unit-test without file I/O.
- Swapping the reader or writer later (e.g., for a different broker format) requires changing only one adapter.

### 2. `openpyxl` + stdlib `csv` instead of `pandas`
We will use `openpyxl` for reading and the standard library `csv` module for writing.

**Rationale:**
- `pandas` is a heavy dependency (~60 MB) and not yet in `pyproject.toml`.
- `openpyxl` is sufficient for reading irregular, multi-section spreadsheets.
- Keeps the dependency footprint minimal.

### 3. Hard-coded symbol mapping with fail-fast
Security names will be mapped via a hard-coded Python dictionary (`core/mapping.py`). If a report contains an unknown name, the tool aborts immediately with a clear error.

**Rationale:**
- The user explicitly chose Option A (hard-coded) over an external config file.
- Fail-fast prevents silently producing an invalid CSV that Snowball would reject.

### 4. `Decimal` for all monetary values
All prices, quantities, fees, and NKD values use `decimal.Decimal`.

**Rationale:**
- Financial calculations must avoid floating-point drift.
- Snowball expects exact decimal values (e.g., per-bond NKD).

### 5. Completed deals as source of truth; uncompleted deals excluded
`Buy`/`Sell` events are derived exclusively from the **deals completed** section. The **deals concluded** section is ignored to avoid duplication, and **deals not completed** are excluded.

**Rationale:**
- Completed deals contain per-trade broker commissions, which we need for the `FeeTax` column.
- Uncompleted deals would create a temporary position mismatch; the user accepted this trade-off.

### 6. Single-threaded CLI, one file at a time
The tool is a single-process CLI (`python -m package_snowball transform-mts input.xlsx output.csv`). No batch mode, no concurrency, no web/API layer.

**Rationale:**
- The user confirmed CLI-only and one-file-at-a-time is sufficient.
- Eliminates complexity around parallel I/O, locking, and partial failures.

### 7. Fail-fast on unsupported row types
If the report contains any row type we do not yet handle (e.g., stock splits, currency conversions), the tool aborts.

**Rationale:**
- The user chose strict behavior (Option a) over silent skipping.
- Guarantees that the output CSV is fully correct or not produced at all.

## Consequences

### Positive
- High testability: each layer can be unit-tested in isolation.
- Clear separation of concerns: parsing, business logic, and I/O do not mix.
- Minimal dependencies: only `openpyxl` added to the project.
- Safe defaults: fail-fast prevents bad data from reaching Snowball.

### Negative / Trade-offs
- Hard-coded mapping requires a code change for every new ticker.
- Fail-fast means the tool cannot produce a "best-effort" partial CSV.
- Uncompleted deals are missing from the output until the next report is processed.
- Dividend per-share price is an approximation based on opening balance (documented heuristic).
