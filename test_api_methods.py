import asyncio
from olymptrade_ws import OlympTradeClient, BalanceAPI, MarketAPI, TradeAPI

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE4MzgwMjEsImlhdCI6MTc1MTY2NTIyMSwiaWQiOjY2MDkwMzUzNSwibmJmIjoxNzUxNjY1MjIxLCJyZXFfY3R4X2hhc2giOiI2NWQ4MTU2MmRiNzBjZDBmY2E5YjMxODgyODBmOWFiYyIsInR5cGUiOiJiZWFyZXIiLCJ1c2VyX2lkIjoxMjg3NTEwNDB9.JmJNOY9Kvgkmg_VUddMvcpG_jolgj_6byJLSoiySC0OpsdyiwCIBfZ6dPK66QwvHJimyBGpKTMssyAmlHPKaetmszy_7QDubiBPS4YNSj0bf9i-vXZ4J1nRjrzk9Xi3bmEPdBM0mDjcuN80kik22MyJYRZQC-eJSDdxb8RQz7rzx2QkXlJb8XOFLAohDYBwwjmc17pncBjfK-8iurPseIMqzIp5sAO23_oG_yCu2gB27pUV88g6qnIobc_S_2zGEIGcK8QNjBoiJgn24n38lncp45Pv6vGavzkBpihUwM_JJhA2kqyIVT701HAO96uf8lfv3-kVcYEn0neplIPunKlgGfB4c3Ynr4JSUo3mbdYk8pxjHN7RIjsY0MN0_1lnf14MoDwrIUKTJEQmD0SZ9aow1u3_lFSHqLMaTSBjuKtuSfX4L3hNBHp_7nvTr1auqRSj9UGd5zLfB3-2t2Tw0dIovWTfBOE_pF3YoW_o74RChF58SKcEVLZVImCsqbHeLMW5NrkQlZjMoz8on-Gf5VPN02WJ5gCTC3QHgc3N-8xyziNgus75NqG0kcmSupmquNjlMWGLHVHwSVnB01wAWyvRZnFGqBHMycT-n2_t_BerZSd2u9C-BKYo3MnpXbbqpKhyrF1JtTCBOfqBolwT1mRZi57rFkulrtISKXxTx69M"  # Replace with your real token

async def test_all_methods():
    client = OlympTradeClient(
        access_token=ACCESS_TOKEN,
        log_raw_messages=True,
        account_id=None,  # Let the client auto-detect
        account_group=None,
        uri=r"wss://ws.olymptrade.com/otp?cid_ver=1&cid_app=web%40OlympTrade%402025.3.26878%4026878&cid_device=%40%40desktop&cid_os=mac_os%4010.15.7"
    )
    await client.start()
    print("Connected!")

    # Initialize session (send all startup messages and get account_id)
    await client.initialize_session()
    print(f"Initialized session. account_id={client.account_id}, account_group={client.account_group}")

    # Wait for balance to be received (poll for up to 10 seconds)
    balance = None
    for _ in range(20):
        balance = client.balance.get_last_balance()
        if balance and 'd' in balance and balance['d']:
            break
        await asyncio.sleep(0.5)
    if balance and 'd' in balance and balance['d']:
        print(f"get_last_balance: {balance}")
    else:
        print("Balance not received after waiting.")

    # 2. MarketAPI (example: subscribe to ticks for EURUSD)
    try:
        await client.market.subscribe_ticks("EURUSD")
        print("Subscribed to EURUSD ticks.")
    except Exception as e:
        print(f"subscribe_ticks failed: {e}")

    # 3. TradeAPI (example: list open trades)
    account_id = client.account_id
    try:
        if account_id:
            open_trades = await client.trade.get_open_trades(account_id)
            print(f"get_open_trades: {open_trades}")
        else:
            print("No account_id found, cannot call get_open_trades.")
    except Exception as e:
        print(f"get_open_trades failed: {e}")

    await client.stop()
    print("Client stopped.")

if __name__ == "__main__":
    asyncio.run(test_all_methods())
