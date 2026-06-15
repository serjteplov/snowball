"""Tests for the MTS report reader."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import openpyxl

from package_snowball.adapters.mts_report_reader import MtsReportReader


def _build_test_workbook(tmp_path: Path) -> Path:
    """Create a minimal MTS-style workbook for testing."""
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None

    # Header rows
    ws.append(["ОТЧЕТ БРОКЕРА"])
    ws.append([])

    # Deals completed section
    ws.append(["Информация о сделках, завершенных в отчетном периоде:"])
    ws.append(
        [
            "Номер сделки",
            "Дата и время заключения",
            "Вид сделки",
            "Контрагент",
            "Наименование ЦБ",
            "Номер гос.регистрации / ISIN",
            "Количество ЦБ, шт.",
            "Цена, ед.вал / %",
            "Валюта цены",
            "Сумма (без НКД)",
            "НКД",
            "Сумма сделки",
            "Валюта платежа",
            "Торговая система",
            "Дата поставки",
            "Дата оплаты ЦБ",
            "Комиссия биржи",
            "Валюта комиссии биржи",
            "Комиссия брокера",
            "Валюта комиссии брокера",
        ]
    )
    ws.append(
        [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
        ]
    )
    ws.append(
        [
            "15222648488",
            "13.01.2026 14:55:37",
            "покупка",
            "НКЦ",
            'ПАО "ЛУКОЙЛ", ао',
            "1-01-00077-A",
            3,
            5404,
            "RUB",
            16212,
            0,
            16212,
            "RUB",
            "МосБиржа",
            "14.01.2026",
            "14.01.2026",
            None,
            None,
            6.49,
            "RUB",
        ]
    )

    # Securities movement section
    ws.append([])
    ws.append(["Информация о движении ценных бумаг"])
    ws.append(
        [
            "Наименование ЦБ",
            "Номер гос.регистрации / ISIN",
            "Входящий остаток, шт.",
            "Зачислено",
            "Списано",
            "Исходящий остаток, шт.",
            "в т.ч. свободно, шт.",
            "Плановый остаток, шт.",
            "Место хранения",
        ]
    )
    ws.append(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
    ws.append(['ПАО "ЛУКОЙЛ", ао', "1-01-00077-A", 0, 5, 0, 5, 5, 6, "НРД"])

    # Cash movement section
    ws.append([])
    ws.append(["Информация о движении денежных средств"])
    ws.append([])
    ws.append(["Входящий остаток денежных средств (RUB):"])
    ws.append(
        ["Дата", "Операция", None, None, None, None, None, "Зачислено RUB", None, "Списано RUB"]
    )
    ws.append(["1", "2", None, None, None, None, None, "3", None, "4"])
    ws.append(["13.01.2026", "Ввод ДС клиента", None, None, None, None, None, 58000, None, 0])
    ws.append(["14.01.2026", "Оплата комиссии брокера", None, None, None, None, None, 0, None, 10])

    path = tmp_path / "test_report.xlsx"
    wb.save(path)
    return path


class TestMtsReportReader:
    """Tests for reading MTS report sections."""

    def test_read_deals_completed(self, tmp_path: Path) -> None:
        path = _build_test_workbook(tmp_path)
        reader = MtsReportReader(path)
        deals, _cash, _balances = reader.read()
        assert len(deals) == 1
        deal = deals[0]
        assert deal.deal_number == "15222648488"
        assert deal.security_name == 'ПАО "ЛУКОЙЛ", ао'
        assert deal.quantity == Decimal("3")
        assert deal.price == Decimal("5404")
        assert deal.broker_commission == Decimal("6.49")

    def test_read_securities_movement(self, tmp_path: Path) -> None:
        path = _build_test_workbook(tmp_path)
        reader = MtsReportReader(path)
        _deals, _cash, balances = reader.read()
        assert len(balances) == 1
        bal = balances[0]
        assert bal.security_name == 'ПАО "ЛУКОЙЛ", ао'
        assert bal.isin == "1-01-00077-A"
        assert bal.opening_balance == Decimal("0")

    def test_read_cash_movements(self, tmp_path: Path) -> None:
        path = _build_test_workbook(tmp_path)
        reader = MtsReportReader(path)
        _deals, cash, _balances = reader.read()
        assert len(cash) == 2
        assert cash[0].operation == "Ввод ДС клиента"
        assert cash[0].credited == Decimal("58000")
        assert cash[0].currency == "RUB"
        assert cash[1].operation == "Оплата комиссии брокера"
        assert cash[1].debited == Decimal("10")

    def test_no_sections_returns_empty(self, tmp_path: Path) -> None:
        wb = openpyxl.Workbook()
        ws = wb.active
        assert ws is not None
        ws.append(["Random header"])
        path = tmp_path / "empty.xlsx"
        wb.save(path)
        reader = MtsReportReader(path)
        deals, cash, balances = reader.read()
        assert deals == []
        assert cash == []
        assert balances == []
