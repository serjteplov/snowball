"""Domain models for MTS to Snowball transformation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class SnowballRow:
    """A single row in the Snowball-compatible output CSV."""

    event: str
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


@dataclass(frozen=True)
class DealCompletedRow:
    """Raw row from the MTS 'deals completed' section."""

    deal_number: str
    deal_date: str
    deal_type: str
    counterparty: str
    security_name: str
    isin: str
    quantity: Decimal
    price: Decimal
    currency: str
    amount_without_nkd: Decimal
    nkd: Decimal
    deal_amount: Decimal
    payment_currency: str
    trading_system: str
    delivery_date: str
    payment_date: str
    exchange_commission: Decimal
    exchange_commission_currency: str
    broker_commission: Decimal
    broker_commission_currency: str


@dataclass(frozen=True)
class CashMovementRow:
    """Raw row from the MTS 'cash movement' section."""

    date: str
    operation: str
    credited: Decimal
    debited: Decimal
    currency: str


@dataclass(frozen=True)
class SecurityBalanceRow:
    """Opening balance from the MTS 'securities movement' section."""

    security_name: str
    isin: str
    opening_balance: Decimal
