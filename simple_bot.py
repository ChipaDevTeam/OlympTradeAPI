import asyncio
from olymptrade_ws import OlympTradeClient
import logging

ACCESS_TOKEN = ""  # Replace with your real token

async def main():
    client = OlympTradeClient(
        access_token=ACCESS_TOKEN,
        log_raw_messages=False,
        uri=r"wss://ws.olymptrade.com/otp?cid_ver=1&cid_app=web%40OlympTrade%402025.3.26878%4026878&cid_device=%40%40desktop&cid_os=mac_os%4010.15.7"
    )
    await client.start()
    print("Connected!")

    try:
        # Get demo account balance
        balance = await client.balance.get_balance()
        print(f"Current balance: {balance}")
        demo_balance = None
        if balance and 'd' in balance and isinstance(balance['d'], list):
            for acc in balance['d']:
                if acc.get('group') == 'demo':
                    demo_balance = acc
                    break
        if not demo_balance:
            print("No demo account found.")
            return
        print(f"Demo account balance: {demo_balance['amount']}")
        print(f"Demo account_id: {demo_balance['account_id']}")

        # Fetch last 10 candles for LATAM_X, 1-minute timeframe
        pair = "LATAM_X"
        candles = await client.market.get_candles(pair, size=60, count=10)
        print(f"Last 10 candles for {pair}: {candles}")

        # Simple strategy: if last candle close > open, buy 'up', else buy 'down'
        if candles and len(candles) > 0:
            last_candle = candles[-1]
            direction = "up" if last_candle.get("close", 0) > last_candle.get("open", 0) else "down"
            print(f"Strategy: Last candle close={last_candle.get('close')}, open={last_candle.get('open')}, direction={direction}")
            print("Placing a demo order based on strategy...")
            order_result = await client.trade.place_order(
                pair=pair,
                amount=1,
                direction=direction,
                duration=60,
                account_id=demo_balance['account_id'],
                group="demo"
            )
            print(f"Order result: {order_result}")
        else:
            print("No candle data available, cannot place order.")
    finally:
        await client.stop()
        print("Client stopped.")

if __name__ == "__main__":
    asyncio.run(main())
