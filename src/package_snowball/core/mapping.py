"""Hard-coded mapping from MTS security names to Snowball symbols.

For stocks and funds, the symbol is the exchange ticker.
For bonds, the symbol is the ISIN. Bonds with duplicate names
(e.g., two issues of the same issuer) are resolved by the
transformer using the ISIN field from the deal row or the cash
movement description text.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# fmt: off
MTS_NAME_TO_TICKER: dict[str, str] = {
    # Stocks
    'ПАО Сбербанк, ап': "SBERP",
    'ПАО "ЛУКОЙЛ", ао': "LKOH",
    'ПАО "НЛМК", ао': "NLMK",
    'ПАО "Северсталь", ао': "CHMF",
    'АО ВИМ Инвестиции Д.У., паи': "RU000A1014L8",
    'МКПАО "ТКС Холдинг", ао': "T",
    'МКПАО "ЯНДЕКС", ао': "YDEX",
    'МКПАО "МД Медикал Груп", ао': "MDMG",
    'Банк ВТБ (ПАО), ао': "VTBR",
    'ПАО "Корпоративный центр ИКС 5", ао': "X5",
    'ПАО "Полюс", ао': "PLZL",
    'МКПАО "Озон", ао': "OZON",
    'АО "ДОМ.РФ", ао': "DOMRF",
    # Bonds (unique names)
    'ОАО "Российские железные дороги", обл.': "RU000A10C8C0",
    'ВЭБ.РФ, обл.': "RU000A10CTX6",
    # Bonds with duplicate names – the transformer resolves these
    # via the ISIN field on the deal row or in the cash description.
    'АО "АТОМЭНЕРГОПРОМ", обл.': "RU000A10C6L5",
    'Министерство финансов Российской Федерации, ОФЗ': "SU26247RMFS5",
}
# fmt: on

_SUFFIXES = (", ао", ", ап", ", обл.", ", паи")


def _strip_suffix(name: str) -> str:
    for suffix in _SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


_STRIPPED_LOOKUP: dict[str, str] = {_strip_suffix(k): v for k, v in MTS_NAME_TO_TICKER.items()}


def map_symbol(name: str) -> str:
    """Return the Snowball symbol for a given MTS security name.

    Args:
        name: Security name as it appears in the MTS report.

    Returns:
        Snowball symbol (ticker for stocks, ISIN for bonds).

    Raises:
        ValueError: If the name is not present in the mapping.
    """
    if name in MTS_NAME_TO_TICKER:
        return MTS_NAME_TO_TICKER[name]

    stripped = _strip_suffix(name)
    if stripped in MTS_NAME_TO_TICKER:
        return MTS_NAME_TO_TICKER[stripped]

    if stripped in _STRIPPED_LOOKUP:
        return _STRIPPED_LOOKUP[stripped]

    logger.warning("Unknown security name: %r — add it to mapping.py", name)
    raise ValueError(f"Unknown security name: {name!r}")
