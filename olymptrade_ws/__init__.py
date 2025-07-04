# olymptrade_ws/__init__.py
# Expose main classes for easy import
from .main import OlympTradeClient
from .core.client import OlympTradeClient as CoreOlympTradeClient
from .api.balance import BalanceAPI
from .api.market import MarketAPI
from .api.trade import TradeAPI

__all__ = [
    "OlympTradeClient",
    "CoreOlympTradeClient",
    "BalanceAPI",
    "MarketAPI",
    "TradeAPI"
]
