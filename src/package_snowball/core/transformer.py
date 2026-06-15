"""Transform raw MTS rows into Snowball-compatible rows."""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from decimal import Decimal

from package_snowball.core.mapping import map_symbol
from package_snowball.core.models import (
    CashMovementRow,
    DealCompletedRow,
    SecurityBalanceRow,
    SnowballRow,
)

logger = logging.getLogger(__name__)

# Regex to extract security name and identifier from parentheses.
# Example: (МКПАО "ТКС Холдинг", 1-01-16784-A)
_DIVIDEND_ID_RE = re.compile(r"\(([^,]+),\s*([^)]+)\)")
# Regex to extract withheld tax amount from dividend description.
# Example: Удержан НДФЛ в размере 14 руб.
_DIVIDEND_TAX_RE = re.compile(r"Удержан НДФЛ в размере ([0-9]+(?:[.,][0-9]+)?) руб")


def _parse_mts_date(raw: str) -> date:
    """Parse DD.MM.YYYY or DD.MM.YYYY HH:MM:SS into a date."""
    day_str = raw.strip().split()[0]
    return datetime.strptime(day_str, "%d.%m.%Y").date()


def _resolve_symbol(security_name: str, isin: str) -> str:
    """Return the Snowball symbol for a security.

    Bonds (identified by an ISIN starting with 'RU') use the ISIN directly.
    Stocks and funds use the hard-coded name-to-ticker mapping.
    """
    if isin.upper().startswith("RU"):
        return isin
    return map_symbol(security_name)


def _format_decimal(value: Decimal) -> Decimal:
    """Normalize a Decimal, avoiding scientific notation and trailing zeros."""
    quantized = value.quantize(Decimal("1.0000000000"))
    s = format(quantized, "f").rstrip("0").rstrip(".")
    return Decimal(s)


class MtsToSnowballTransformer:
    """Convert raw MTS rows into Snowball rows."""

    def transform_deals(self, deals: list[DealCompletedRow]) -> list[SnowballRow]:
        """Transform completed deals into Buy / Sell rows."""
        result: list[SnowballRow] = []
        for deal in deals:
            deal_type = deal.deal_type.strip().lower()
            if deal_type == "покупка":
                event = "Buy"
            elif deal_type == "продажа":
                event = "Sell"
            else:
                raise ValueError(f"Unsupported deal type: {deal.deal_type!r}")
            symbol = _resolve_symbol(deal.security_name, deal.isin)
            nkd = Decimal("0")
            if deal.nkd != Decimal("0"):
                if deal.quantity == Decimal("0"):
                    logger.warning(
                        "Zero-quantity bond deal %s: NKD set to 0",
                        deal.deal_number,
                    )
                else:
                    nkd = _format_decimal(deal.nkd / deal.quantity)
            result.append(
                SnowballRow(
                    event=event,
                    date=_parse_mts_date(deal.deal_date),
                    symbol=symbol,
                    price=_format_decimal(deal.price),
                    quantity=_format_decimal(deal.quantity),
                    currency=deal.payment_currency,
                    fee_tax=_format_decimal(deal.broker_commission),
                    exchange="MCX",
                    nkd=nkd,
                    fee_currency=deal.broker_commission_currency,
                    note=deal.deal_number,
                )
            )
        return result

    def transform_cash_movements(
        self,
        cash_rows: list[CashMovementRow],
        balances: list[SecurityBalanceRow],
        deals: list[DealCompletedRow],
    ) -> list[SnowballRow]:
        """Transform cash movement rows into Snowball events."""
        result: list[SnowballRow] = []
        balance_lookup = {b.isin: b.opening_balance for b in balances}

        # Pre-calculate total broker commissions per payment date for fee attribution.
        commission_by_date: dict[str, Decimal] = {}
        for deal in deals:
            d = _parse_mts_date(deal.payment_date)
            key = d.isoformat()
            commission_by_date[key] = (
                commission_by_date.get(key, Decimal("0")) + deal.broker_commission
            )

        for row in cash_rows:
            op = row.operation.strip()
            row_date = _parse_mts_date(row.date)

            if op == "Ввод ДС клиента":
                result.append(
                    SnowballRow(
                        event="Cash_In",
                        date=row_date,
                        symbol=row.currency,
                        price=Decimal("1"),
                        quantity=_format_decimal(row.credited),
                        currency=row.currency,
                        fee_tax=Decimal("0"),
                    )
                )
            elif op == "Вывод ДС клиента":
                result.append(
                    SnowballRow(
                        event="Cash_Out",
                        date=row_date,
                        symbol=row.currency,
                        price=Decimal("1"),
                        quantity=_format_decimal(row.debited),
                        currency=row.currency,
                        fee_tax=Decimal("0"),
                    )
                )
            elif op.startswith("Получение дивидендов/дохода по паям"):
                result.extend(self._parse_dividend(row, row_date, balance_lookup))
            elif op.startswith("Погашение купона"):
                result.extend(self._parse_coupon(row, row_date, balance_lookup))
            elif op == "Оплата комиссии брокера":
                fee_row = self._handle_commission(row, row_date, commission_by_date)
                if fee_row is not None:
                    result.append(fee_row)
            elif op == "Удержание НДФЛ":
                result.append(
                    SnowballRow(
                        event="Cash_Expense",
                        date=row_date,
                        symbol=row.currency,
                        price=Decimal("1"),
                        quantity=_format_decimal(row.debited),
                        currency=row.currency,
                        fee_tax=Decimal("0"),
                        note="НДФЛ",
                    )
                )
            elif op == "Оплата по сделке":
                # Cash settlement for trades; already reflected in Buy/Sell rows.
                continue
            else:
                raise ValueError(f"Unsupported cash movement operation: {op!r}")

        return result

    def _parse_dividend(
        self,
        row: CashMovementRow,
        row_date: date,
        balance_lookup: dict[str, Decimal],
    ) -> list[SnowballRow]:
        """Parse a dividend description and emit Dividend rows."""
        tax_match = _DIVIDEND_TAX_RE.search(row.operation)
        tax = Decimal("0")
        if tax_match:
            tax = Decimal(tax_match.group(1).replace(",", "."))

        gross = row.credited + tax
        symbol, balance = self._resolve_dividend_symbol_and_balance(row.operation, balance_lookup)

        price = Decimal("0")
        if balance and balance > Decimal("0"):
            price = _format_decimal(gross / balance)
        else:
            logger.warning(
                "Dividend on %s: opening balance unknown for %s, Price set to 0",
                row_date.isoformat(),
                symbol,
            )

        return [
            SnowballRow(
                event="Dividend",
                date=row_date,
                symbol=symbol,
                price=price,
                quantity=_format_decimal(gross),
                currency=row.currency,
                fee_tax=_format_decimal(tax),
                note=row.operation,
            )
        ]

    def _parse_coupon(
        self,
        row: CashMovementRow,
        row_date: date,
        balance_lookup: dict[str, Decimal],
    ) -> list[SnowballRow]:
        """Parse a bond coupon description and emit Dividend rows."""
        symbol, balance = self._resolve_dividend_symbol_and_balance(row.operation, balance_lookup)

        price = Decimal("0")
        if balance and balance > Decimal("0"):
            price = _format_decimal(row.credited / balance)
        else:
            logger.warning(
                "Coupon on %s: opening balance unknown for %s, Price set to 0",
                row_date.isoformat(),
                symbol,
            )

        return [
            SnowballRow(
                event="Dividend",
                date=row_date,
                symbol=symbol,
                price=price,
                quantity=_format_decimal(row.credited),
                currency=row.currency,
                fee_tax=Decimal("0"),
                note=row.operation,
            )
        ]

    def _resolve_dividend_symbol_and_balance(
        self,
        description: str,
        balance_lookup: dict[str, Decimal],
    ) -> tuple[str, Decimal | None]:
        """Extract symbol and opening balance from a dividend/coupon description."""
        match = _DIVIDEND_ID_RE.search(description)
        if not match:
            raise ValueError(f"Cannot parse dividend/coupon description: {description!r}")

        security_name = match.group(1).strip()
        identifier = match.group(2).strip()

        symbol = identifier if identifier.upper().startswith("RU") else map_symbol(security_name)

        balance = balance_lookup.get(identifier)

        return symbol, balance

    def _handle_commission(
        self,
        row: CashMovementRow,
        row_date: date,
        commission_by_date: dict[str, Decimal],
    ) -> SnowballRow | None:
        """Handle a broker commission cash row.

        Returns a Fee row if the cash commission exceeds the sum of
        trade commissions for the same date (orphan fee); otherwise None.
        """
        row_date_str = row_date.isoformat()
        trade_commissions = commission_by_date.get(row_date_str, Decimal("0"))
        cash_commission = row.debited

        if cash_commission > trade_commissions:
            excess = cash_commission - trade_commissions
            logger.warning(
                "Unmatched broker fee on %s: %s (cash %s vs trades %s)",
                row_date_str,
                excess,
                cash_commission,
                trade_commissions,
            )
            return SnowballRow(
                event="Fee",
                date=row_date,
                symbol="",
                price=Decimal("0"),
                quantity=Decimal("0"),
                currency=row.currency,
                fee_tax=_format_decimal(excess),
                note="Broker fee (unmatched)",
            )

        if cash_commission < trade_commissions:
            logger.warning(
                "Cash commission %s is less than trade commissions %s on %s",
                cash_commission,
                trade_commissions,
                row_date_str,
            )

        return None
