# SPEC: MTS → Snowball Brokerage Report Transformer

## Goal
Provide a single-file CLI that converts one MTS brokerage report (`.xlsx`) into one Snowball-compatible CSV (`.csv`).

## Functional rules

### Input / output
- **Input:** one `.xlsx` file, single sheet (`Лист1`), MTS broker report format.
- **Output:** one `.csv` file, UTF-8 with BOM, comma-separated, including header row.

### Sections used
- **Deals completed** (`Информация о сделках, завершенных в отчетном периоде`) → `Buy` / `Sell`.
- **Cash movement** (`Информация о движении денежных средств`) → `Cash_In`, `Cash_Out`, `Dividend`, `Fee`, `Cash_Expense`.
- **Securities movement** (`Информация о движении ценных бумаг`) → opening balances for dividend per-share heuristic only.

### Sections ignored
- Deals concluded, deals not completed, report header/footer, summary balances.

### Event mapping
| MTS source | Snowball event | Notes |
|---|---|---|
| `покупка` in deals completed | `Buy` | |
| `продажа` in deals completed | `Sell` | |
| `Ввод ДС клиента` in cash movement | `Cash_In` | `Symbol` = currency, `Price` = 1, `Quantity` = credited amount |
| `Вывод ДС клиента` in cash movement | `Cash_Out` | `Symbol` = currency, `Price` = 1, `Quantity` = debited amount |
| `Получение дивидендов/дохода по паям` in cash movement | `Dividend` | Parse text for ISIN and tax. `FeeTax` = withheld tax. `Note` = raw description. |
| `Погашение купона` in cash movement | `Dividend` | Same as above; bond coupons are Snowball `Dividend` events. |
| `Оплата комиссии брокера` in cash movement | `Fee` | **Only if** the cash amount exceeds the sum of trade commissions for that same date. |
| `Удержание НДФЛ` in cash movement | `Cash_Expense` | `Symbol` = currency, `Price` = 1, `Quantity` = tax amount, `Note` = "НДФЛ" |

### Field derivation
- **Symbol mapping:** hard-coded `dict[str, str]` (`MTS_NAME_TO_TICKER`). Fail fast (`ValueError`) on unknown names.
- **Date:** parse `DD.MM.YYYY` (or `DD.MM.YYYY HH:MM:SS`) → `YYYY-MM-DD`.
- **Price / Quantity / FeeTax / NKD:** use `Decimal` everywhere. No floats.
- **NKD (bonds):** `total_nkd / quantity`. If `quantity == 0`, emit `NKD = 0` and log a warning.
- **Fee attribution (orphan fees):**
  1. Group completed deals by **payment date**.
  2. Sum broker commissions per date.
  3. For each cash-movement commission row on that date:
     - If cash commission ≤ summed trade commissions → ignore (already in `Buy`/`Sell.FeeTax`).
     - If cash commission > summed trade commissions → emit `Fee` event for the excess.
- **Dividend per-share heuristic:**
  - `gross = credited + tax` (when tax is explicit in the description text).
  - `Price = gross / opening_balance` from securities movement.
  - `Quantity = gross`.
  - If opening balance is unknown, `Price = 0` and a warning is logged.
- **Exchange:** `МосБиржа` → `MCX`.
- **FeeCurrency:** taken from MTS commission currency column if it differs from deal currency; otherwise empty.
- **DoNotAdjustCash:** always empty / `False`.
- **Note:**
  - `Buy` / `Sell`: original MTS deal number.
  - `Dividend`: raw Russian operation description.
  - `Fee` / `Cash_Expense`: short descriptive note.

### Error handling
- Unknown security name → fail fast with clear message.
- Unknown row type / unsupported event in any section → fail fast.
- All errors print to `stderr` and return a non-zero exit code.

## Data model

### Public output model
```python
@dataclass(frozen=True)
class SnowballRow:
    event: str               # e.g. "Buy", "Dividend"
    date: date
    symbol: str
    price: Decimal
    quantity: Decimal
    currency: str
    fee_tax: Decimal
    exchange: str = ""
    nkd: Decimal = Decimal("0")
    fee_currency: str = ""
    do_not_adjust_cash: bool = False
    note: str = ""
```

### Internal raw models
- `DealCompletedRow` — flat dataclass mirroring the MTS deals-completed columns.
- `CashMovementRow` — flat dataclass mirroring the MTS cash-movement columns.
- `SecurityBalanceRow` — security name, ISIN/reg-number, opening balance.

## Concurrency approach
- Single-threaded, single-process.
- One input file per invocation.
- No shared mutable state; each run is independent.

## API behavior
- **Interface:** CLI only.
- **Command:** `python -m package_snowball transform-mts <input.xlsx> <output.csv>`
- **Arguments:** two positional paths (input, output).
- **Overwrite:** allow overwriting existing output file.
- **Logging:** errors to `stderr`; success is silent (optional single-line confirmation to `stdout`).
- **No flags** for verbosity, config files, or batch mode.

## Events

### Buy / Sell
Derived from deals completed.
- `Price` = unit price per share/bond.
- `Quantity` = number of securities.
- `Currency` = payment currency.
- `FeeTax` = broker commission for this trade.
- `NKD` = per-bond accrued interest (bonds only).
- `FeeCurrency` = commission currency if different from `Currency`.
- `Exchange` = `MCX`.
- `Note` = MTS deal number.

### Dividend (includes bond coupons)
Derived from cash movement dividend/coupon rows.
- `Symbol` = mapped ticker (stocks) or ISIN (bonds).
- `Price` = dividend per share (`gross / opening_balance`), or `0` if balance unknown.
- `Quantity` = total gross amount.
- `Currency` = currency of credit.
- `FeeTax` = tax withheld (parsed from description text, or `0` for coupons where tax is in a separate row).
- `Note` = raw MTS operation description.

### Fee
Derived from unmatched broker commission in cash movement.
- `Symbol` = empty string.
- `Price` = `0`.
- `Quantity` = `0`.
- `Currency` = commission currency.
- `FeeTax` = excess commission amount.
- `Note` = `"Broker fee (unmatched)"`.

### Cash_In / Cash_Out
Derived from cash movement in/out rows.
- `Symbol` = currency code (e.g. `RUB`).
- `Price` = `1`.
- `Quantity` = amount.
- `Currency` = same as `Symbol`.
- `FeeTax` = `0`.

### Cash_Expense
Derived from `Удержание НДФЛ` rows.
- `Symbol` = currency code.
- `Price` = `1`.
- `Quantity` = tax amount.
- `Currency` = same as `Symbol`.
- `FeeTax` = `0`.
- `Note` = `"НДФЛ"`.

## Tests
- **Framework:** pytest.
- **Style:** pure unit tests; no golden-file / end-to-end fixtures.
- **Coverage targets:**
  - Symbol mapping (known hit, unknown fail-fast).
  - Date parsing (date only, date+time, invalid).
  - NKD calculation (normal, zero-quantity fallback).
  - Fee attribution (perfect match, orphan excess, missing cash row).
  - Dividend text parsing (with explicit tax, without tax, malformed).
  - Event type detection from cash-movement operation strings.
  - Decimal precision (no float drift).
  - Error handling for unsupported row types (must raise).
- **Mocking:** pass plain Python lists/dicts of raw row data directly to transformer functions; no `.xlsx` I/O in unit tests.

## Non-goals
- Support for brokers other than MTS.
- Batch or multi-file processing.
- GUI, web interface, or REST API.
- External ticker/ISIN lookup service.
- Handling `Stock_As_Dividend`, `Split`, `Spinoff`, `Amortisation`, `Repayment`, `Cash_Convert` (no samples available).
- Portfolio consistency validation (e.g., verifying that cash balances reconcile).
- Automatic correction of data errors in the MTS report.
- Configuration file for symbol mapping (hard-coded dict only).
