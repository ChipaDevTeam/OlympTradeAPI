# REFERENCE.md

# OlympTradeAPI Python Reference

This document describes all public classes and functions in the OlympTradeAPI package, with real usage examples.

---

## Quick Start Example

```python
import asyncio
from olymptrade_ws import OlympTradeClient

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

async def main():
    client = OlympTradeClient(access_token=ACCESS_TOKEN)
    await client.start()

    # Get demo account balance (auto-initializes session)
    balance = await client.balance.get_balance()
    print("Balance message:", balance)
    demo_acc = next(acc for acc in balance['d'] if acc['group'] == 'demo')
    print("Demo account balance:", demo_acc['amount'])

    # Get last 10 candles for LATAM_X, 1-minute timeframe
    candles = await client.market.get_candles("LATAM_X", size=60, count=10)
    print("Candles:", candles)

    # Place a demo order based on last candle
    last_candle = candles[-1]
    direction = "up" if last_candle['close'] > last_candle['open'] else "down"
    order_result = await client.trade.place_order(
        pair="LATAM_X",
        amount=1,
        direction=direction,
        duration=60,
        account_id=demo_acc['account_id'],
        group="demo"
    )
    print("Order result:", order_result)

    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Main Classes & Methods

### OlympTradeClient
- **Create a client:**
    ```python
    client = OlympTradeClient(access_token="YOUR_TOKEN")
    await client.start()
    ```
- **Attributes:**
    - `balance`: Access to balance API
    - `market`: Access to market API
    - `trade`: Access to trade API

### BalanceAPI
- **Get balance (auto-initializes session):**
    ```python
    balance = await client.balance.get_balance()
    ```
- **Get last received balance (no wait):**
    ```python
    last = client.balance.get_last_balance()
    ```
- **Request balance directly (rarely needed):**
    ```python
    await client.balance.request_balance(account_id)
    ```

### MarketAPI
- **Get candles:**
    ```python
    candles = await client.market.get_candles("LATAM_X", size=60, count=10)
    ```
- **Subscribe to ticks:**
    ```python
    await client.market.subscribe_ticks("LATAM_X")
    ```

### TradeAPI
- **Place an order:**
    ```python
    result = await client.trade.place_order(
        pair="LATAM_X",
        amount=1,
        direction="up",
        duration=60,
        account_id=demo_acc['account_id'],
        group="demo"
    )
    ```
- **Get open trades:**
    ```python
    open_trades = await client.trade.get_open_trades(account_id, group="demo")
    ```

---

## Notes
- All async methods must be awaited.
- You must call `await client.start()` before using API methods.
- `get_balance()` will handle all session initialization and subscriptions for you.
- See the code for more advanced usage and event handling.

---

For more details, see the docstrings in each class and method.
