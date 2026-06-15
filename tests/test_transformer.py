"""Tests for the MTS to Snowball transformer."""

from __future__ import annotations

import logging
from datetime import date
from decimal import Decimal
from typing import Any

import pytest

from package_snowball.core.models import (
    CashMovementRow,
    DealCompletedRow,
    SecurityBalanceRow,
)
from package_snowball.core.transformer import MtsToSnowballTransformer


def _deal(**kwargs: Any) -> DealCompletedRow:
    """Build a DealCompletedRow with sensible defaults."""
    defaults: dict[str, Any] = {
        "deal_number": "1",
        "deal_date": "13.01.2026 14:55:37",
        "deal_type": "покупка",
        "counterparty": "НКЦ",
        "security_name": 'ПАО "ЛУКОЙЛ", ао',
        "isin": "1-01-00077-A",
        "quantity": Decimal("3"),
        "price": Decimal("5404"),
        "currency": "RUB",
        "amount_without_nkd": Decimal("16212"),
        "nkd": Decimal("0"),
        "deal_amount": Decimal("16212"),
        "payment_currency": "RUB",
        "trading_system": "МосБиржа",
        "delivery_date": "14.01.2026",
        "payment_date": "14.01.2026",
        "exchange_commission": Decimal("0"),
        "exchange_commission_currency": "",
        "broker_commission": Decimal("6.49"),
        "broker_commission_currency": "RUB",
    }
    defaults.update(kwargs)
    return DealCompletedRow(**defaults)


def _cash(**kwargs: Any) -> CashMovementRow:
    """Build a CashMovementRow with sensible defaults."""
    defaults: dict[str, Any] = {
        "date": "14.01.2026",
        "operation": "Ввод ДС клиента",
        "credited": Decimal("1000"),
        "debited": Decimal("0"),
        "currency": "RUB",
    }
    defaults.update(kwargs)
    return CashMovementRow(**defaults)


def _balance(**kwargs: Any) -> SecurityBalanceRow:
    """Build a SecurityBalanceRow with sensible defaults."""
    defaults: dict[str, Any] = {
        "security_name": 'ПАО "ЛУКОЙЛ", ао',
        "isin": "1-01-00077-A",
        "opening_balance": Decimal("10"),
    }
    defaults.update(kwargs)
    return SecurityBalanceRow(**defaults)


class TestTransformDeals:
    """Tests for transforming completed deals into Buy/Sell rows."""

    def test_buy_basic(self) -> None:
        deal = _deal()
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert len(rows) == 1
        row = rows[0]
        assert row.event == "Buy"
        assert row.date == date(2026, 1, 13)
        assert row.symbol == "LKOH"
        assert row.price == Decimal("5404")
        assert row.quantity == Decimal("3")
        assert row.currency == "RUB"
        assert row.fee_tax == Decimal("6.49")
        assert row.exchange == "MCX"
        assert row.nkd == Decimal("0")
        assert row.note == "1"

    def test_sell_basic(self) -> None:
        deal = _deal(deal_type="продажа")
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert len(rows) == 1
        row = rows[0]
        assert row.event == "Sell"
        assert row.date == date(2026, 1, 13)
        assert row.symbol == "LKOH"
        assert row.price == Decimal("5404")
        assert row.quantity == Decimal("3")
        assert row.currency == "RUB"
        assert row.fee_tax == Decimal("6.49")
        assert row.exchange == "MCX"

    def test_unknown_deal_type_raises(self) -> None:
        deal = _deal(deal_type="репо")
        transformer = MtsToSnowballTransformer()
        with pytest.raises(ValueError, match="Unsupported deal type"):
            transformer.transform_deals([deal])

    def test_invalid_date_raises(self) -> None:
        deal = _deal(deal_date="not-a-date")
        transformer = MtsToSnowballTransformer()
        with pytest.raises(ValueError, match="does not match format"):
            transformer.transform_deals([deal])

    def test_bond_uses_isin(self) -> None:
        deal = _deal(
            security_name='АО "АТОМЭНЕРГОПРОМ", обл.',
            isin="RU000A10C6L5",
            price=Decimal("98"),
            quantity=Decimal("1"),
            nkd=Decimal("28.7"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert rows[0].symbol == "RU000A10C6L5"

    def test_nkd_normal(self) -> None:
        deal = _deal(
            security_name='АО "АТОМЭНЕРГОПРОМ", обл.',
            isin="RU000A10C6L5",
            quantity=Decimal("10"),
            nkd=Decimal("28.7"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert rows[0].nkd == Decimal("2.87")

    def test_nkd_zero_quantity_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.WARNING)
        deal = _deal(
            security_name='АО "АТОМЭНЕРГОПРОМ", обл.',
            isin="RU000A10C6L5",
            quantity=Decimal("0"),
            nkd=Decimal("28.7"),
            deal_number="ZERO",
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert rows[0].nkd == Decimal("0")
        assert "Zero-quantity bond deal ZERO" in caplog.text

    def test_decimal_precision(self) -> None:
        deal = _deal(price=Decimal("87.412"), quantity=Decimal("25"))
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_deals([deal])
        assert rows[0].price == Decimal("87.412")


class TestTransformCashMovements:
    """Tests for transforming cash movement rows."""

    def test_cash_in(self) -> None:
        cash = _cash(operation="Ввод ДС клиента", credited=Decimal("58000"))
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [])
        assert len(rows) == 1
        assert rows[0].event == "Cash_In"
        assert rows[0].quantity == Decimal("58000")
        assert rows[0].symbol == "RUB"
        assert rows[0].price == Decimal("1")

    def test_cash_out(self) -> None:
        cash = _cash(operation="Вывод ДС клиента", debited=Decimal("1140"))
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [])
        assert rows[0].event == "Cash_Out"
        assert rows[0].quantity == Decimal("1140")

    def test_deal_payment_ignored(self) -> None:
        cash = _cash(operation="Оплата по сделке", debited=Decimal("1000"))
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [])
        assert len(rows) == 0

    def test_unsupported_operation_raises(self) -> None:
        cash = _cash(operation="Неизвестная операция")
        transformer = MtsToSnowballTransformer()
        with pytest.raises(ValueError, match="Unsupported cash movement operation"):
            transformer.transform_cash_movements([cash], [], [])

    def test_cash_expense(self) -> None:
        cash = _cash(
            operation="Удержание НДФЛ",
            debited=Decimal("84"),
            credited=Decimal("0"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [])
        assert len(rows) == 1
        assert rows[0].event == "Cash_Expense"
        assert rows[0].quantity == Decimal("84")
        assert rows[0].note == "НДФЛ"


class TestDividendsAndCoupons:
    """Tests for dividend and coupon parsing."""

    def test_dividend_with_tax(self) -> None:
        cash = _cash(
            operation=(
                "Получение дивидендов/дохода по паям"
                ' (МКПАО "ТКС Холдинг", 1-01-16784-A).'
                " Удержан НДФЛ в размере 14 руб."
            ),
            credited=Decimal("94"),
        )
        balance = _balance(
            security_name='МКПАО "ТКС Холдинг", ао',
            isin="1-01-16784-A",
            opening_balance=Decimal("3"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [balance], [])
        assert len(rows) == 1
        row = rows[0]
        assert row.event == "Dividend"
        assert row.symbol == "T"
        assert row.quantity == Decimal("108")
        assert row.fee_tax == Decimal("14")
        assert row.price == Decimal("36")
        assert row.note == cash.operation

    def test_dividend_unknown_balance_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.WARNING)
        cash = _cash(
            operation=(
                "Получение дивидендов/дохода по паям"
                ' (МКПАО "ТКС Холдинг", 1-01-16784-A).'
                " Удержан НДФЛ в размере 14 руб."
            ),
            credited=Decimal("94"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [])
        assert rows[0].price == Decimal("0")
        assert "opening balance unknown" in caplog.text

    def test_coupon_no_tax(self) -> None:
        cash = _cash(
            operation='Погашение купона (АО "АТОМЭНЕРГОПРОМ", RU000A10C6L5)',
            credited=Decimal("21897.36"),
        )
        balance = _balance(
            security_name='АО "АТОМЭНЕРГОПРОМ", обл.',
            isin="RU000A10C6L5",
            opening_balance=Decimal("612"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [balance], [])
        assert len(rows) == 1
        row = rows[0]
        assert row.event == "Dividend"
        assert row.symbol == "RU000A10C6L5"
        assert row.quantity == Decimal("21897.36")
        assert row.fee_tax == Decimal("0")

    def test_dividend_malformed_raises(self) -> None:
        cash = _cash(operation="Получение дивидендов/дохода по паям (без данных)")
        transformer = MtsToSnowballTransformer()
        with pytest.raises(ValueError, match="Cannot parse dividend/coupon description"):
            transformer.transform_cash_movements([cash], [], [])


class TestFeeAttribution:
    """Tests for broker commission fee attribution."""

    def test_matched_commission_no_fee(self) -> None:
        deal = _deal(
            payment_date="14.01.2026",
            broker_commission=Decimal("10"),
        )
        cash = _cash(
            operation="Оплата комиссии брокера",
            debited=Decimal("10"),
            date="14.01.2026",
            credited=Decimal("0"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [deal])
        assert len(rows) == 0

    def test_orphan_fee_emits_fee(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.WARNING)
        deal = _deal(
            payment_date="14.01.2026",
            broker_commission=Decimal("5"),
        )
        cash = _cash(
            operation="Оплата комиссии брокера",
            debited=Decimal("15"),
            date="14.01.2026",
            credited=Decimal("0"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [deal])
        assert len(rows) == 1
        assert rows[0].event == "Fee"
        assert rows[0].fee_tax == Decimal("10")
        assert "Unmatched broker fee" in caplog.text

    def test_commission_shortfall_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.WARNING)
        deal = _deal(
            payment_date="14.01.2026",
            broker_commission=Decimal("20"),
        )
        cash = _cash(
            operation="Оплата комиссии брокера",
            debited=Decimal("10"),
            date="14.01.2026",
            credited=Decimal("0"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [deal])
        assert len(rows) == 0
        assert "Cash commission 10 is less than trade commissions 20" in caplog.text

    def test_multiple_deals_same_date_fee_attribution(self) -> None:
        deal1 = _deal(
            payment_date="14.01.2026",
            broker_commission=Decimal("5"),
        )
        deal2 = _deal(
            payment_date="14.01.2026",
            broker_commission=Decimal("7"),
        )
        cash = _cash(
            operation="Оплата комиссии брокера",
            debited=Decimal("15"),
            date="14.01.2026",
            credited=Decimal("0"),
        )
        transformer = MtsToSnowballTransformer()
        rows = transformer.transform_cash_movements([cash], [], [deal1, deal2])
        assert len(rows) == 1
        assert rows[0].event == "Fee"
        assert rows[0].fee_tax == Decimal("3")
