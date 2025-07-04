import asyncio
from olymptrade_ws import OlympTradeClient
import logging

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE4MzgwMjEsImlhdCI6MTc1MTY2NTIyMSwiaWQiOjY2MDkwMzUzNSwibmJmIjoxNzUxNjY1MjIxLCJyZXFfY3R4X2hhc2giOiI2NWQ4MTU2MmRiNzBjZDBmY2E5YjMxODgyODBmOWFiYyIsInR5cGUiOiJiZWFyZXIiLCJ1c2VyX2lkIjoxMjg3NTEwNDB9.JmJNOY9Kvgkmg_VUddMvcpG_jolgj_6byJLSoiySC0OpsdyiwCIBfZ6dPK66QwvHJimyBGpKTMssyAmlHPKaetmszy_7QDubiBPS4YNSj0bf9i-vXZ4J1nRjrzk9Xi3bmEPdBM0mDjcuN80kik22MyJYRZQC-eJSDdxb8RQz7rzx2QkXlJb8XOFLAohDYBwwjmc17pncBjfK-8iurPseIMqzIp5sAO23_oG_yCu2gB27pUV88g6qnIobc_S_2zGEIGcK8QNjBoiJgn24n38lncp45Pv6vGavzkBpihUwM_JJhA2kqyIVT701HAO96uf8lfv3-kVcYEn0neplIPunKlgGfB4c3Ynr4JSUo3mbdYk8pxjHN7RIjsY0MN0_1lnf14MoDwrIUKTJEQmD0SZ9aow1u3_lFSHqLMaTSBjuKtuSfX4L3hNBHp_7nvTr1auqRSj9UGd5zLfB3-2t2Tw0dIovWTfBOE_pF3YoW_o74RChF58SKcEVLZVImCsqbHeLMW5NrkQlZjMoz8on-Gf5VPN02WJ5gCTC3QHgc3N-8xyziNgus75NqG0kcmSupmquNjlMWGLHVHwSVnB01wAWyvRZnFGqBHMycT-n2_t_BerZSd2u9C-BKYo3MnpXbbqpKhyrF1JtTCBOfqBolwT1mRZi57rFkulrtISKXxTx69M"  # Replace with your real token

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
