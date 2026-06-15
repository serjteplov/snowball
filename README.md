# snowball

MTS brokerage report to Snowball CSV transformer.

## Usage

Convert a single MTS report:

```bash
python -m package_snowball transform-mts input.xlsx output.csv
```

A sample report is available at `docs/examples/input/1388701_01012026-31012026.xlsx`.

## Development

Create a virtual environment and install dependencies:

```bash
make setup
```

Or, if you already have a virtual environment:

```bash
make install-dev
```

Run all checks:

```bash
make check
```

## Commands

- `make format` — run ruff formatter
- `make lint` — run ruff linter
- `make typecheck` — run mypy
- `make test` — run pytest
- `make check` — run all of the above

## Snowball CSV format reference

The output follows the Snowball portfolio aggregator schema. Supported events:

| Event | Description |
|---|---|
| Buy | Purchase of stocks or bonds |
| Sell | Sale of stocks or bonds |
| Dividend | Dividends or bond coupons |
| Fee | Unmatched broker commission |
| Cash_In | Account deposit |
| Cash_Out | Account withdrawal |
| Cash_Expense | Tax withholding (НДФЛ) |

For full column definitions, see `docs/examples/output/CSV_Template.csv`.
