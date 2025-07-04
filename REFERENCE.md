# REFERENCE.md

# OlympTradeAPI Python Reference

This document describes all public classes and functions in the OlympTradeAPI package, with usage examples.

---

## Main Classes

### OlympTradeClient
- **Location:** `from olymptrade_ws import OlympTradeClient`
- **Description:** Main client for connecting to the Olymp Trade WebSocket API.
- **Usage:**
    ```python
    from olymptrade_ws import OlympTradeClient
    client = OlympTradeClient(access_token="YOUR_TOKEN")
    ```
- **Key Methods:**
    - `await client.start()`: Connects and starts the client.
    - `await client.stop()`: Stops the client and disconnects.
    - `client.balance`: Access to balance API (see below).
    - `client.market`: Access to market API.
    - `client.trade`: Access to trade API.

### BalanceAPI
- **Location:** `from olymptrade_ws import BalanceAPI`
- **Description:** Handles balance subscriptions and queries.
- **Usage:**
    ```python
    balance_api = client.balance
    await balance_api.subscribe_balance_updates()
    balance = balance_api.get_last_balance()
    ```
- **Key Methods:**
    - `await subscribe_balance_updates()`: Subscribe to real-time balance updates.
    - `get_last_balance()`: Get the most recent balance received.
    - `await request_balance(account_id, group="real")`: Explicitly request balance (may not always work).

### MarketAPI
- **Location:** `from olymptrade_ws import MarketAPI`
- **Description:** Handles market data (ticks, candles, etc).
- **Usage:**
    ```python
    market_api = client.market
    await market_api.subscribe_ticks("EURUSD")
    ```
- **Key Methods:**
    - `await subscribe_ticks(pair)`: Subscribe to live price ticks for a pair.
    - `await unsubscribe_ticks(pair)`: Unsubscribe from live price ticks.
    - `await get_candles(pair, interval, count)`: Get historical candle data.

### TradeAPI
- **Location:** `from olymptrade_ws import TradeAPI`
- **Description:** Handles trade placement and updates.
- **Usage:**
    ```python
    trade_api = client.trade
    await trade_api.place_trade(pair, amount, direction, duration)
    ```
- **Key Methods:**
    - `await place_trade(pair, amount, direction, duration)`: Place a new trade.
    - `await get_open_trades()`: Get currently open trades.
    - `await close_trade(trade_id)`: Close a trade by ID.

---

## Event Callbacks

You can register callbacks for events (e.g., balance updates, trade updates) using the client’s event system. See the code for details.

---

## Notes
- All async methods must be awaited.
- You must start the client (`await client.start()`) before using API methods.
- See the code for more advanced usage and event handling.

---

For more details, see the docstrings in each class and method.
