from olymptrade_ws.main import OlympTradeClient

def main():

    client = OlympTradeClient(
        access_token='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTE4MzgwMjEsImlhdCI6MTc1MTY2NTIyMSwiaWQiOjY2MDkwMzUzNSwibmJmIjoxNzUxNjY1MjIxLCJyZXFfY3R4X2hhc2giOiI2NWQ4MTU2MmRiNzBjZDBmY2E5YjMxODgyODBmOWFiYyIsInR5cGUiOiJiZWFyZXIiLCJ1c2VyX2lkIjoxMjg3NTEwNDB9.JmJNOY9Kvgkmg_VUddMvcpG_jolgj_6byJLSoiySC0OpsdyiwCIBfZ6dPK66QwvHJimyBGpKTMssyAmlHPKaetmszy_7QDubiBPS4YNSj0bf9i-vXZ4J1nRjrzk9Xi3bmEPdBM0mDjcuN80kik22MyJYRZQC-eJSDdxb8RQz7rzx2QkXlJb8XOFLAohDYBwwjmc17pncBjfK-8iurPseIMqzIp5sAO23_oG_yCu2gB27pUV88g6qnIobc_S_2zGEIGcK8QNjBoiJgn24n38lncp45Pv6vGavzkBpihUwM_JJhA2kqyIVT701HAO96uf8lfv3-kVcYEn0neplIPunKlgGfB4c3Ynr4JSUo3mbdYk8pxjHN7RIjsY0MN0_1lnf14MoDwrIUKTJEQmD0SZ9aow1u3_lFSHqLMaTSBjuKtuSfX4L3hNBHp_7nvTr1auqRSj9UGd5zLfB3-2t2Tw0dIovWTfBOE_pF3YoW_o74RChF58SKcEVLZVImCsqbHeLMW5NrkQlZjMoz8on-Gf5VPN02WJ5gCTC3QHgc3N-8xyziNgus75NqG0kcmSupmquNjlMWGLHVHwSVnB01wAWyvRZnFGqBHMycT-n2_t_BerZSd2u9C-BKYo3MnpXbbqpKhyrF1JtTCBOfqBolwT1mRZi57rFkulrtISKXxTx69M'
    )

    client.connection.connect()
    
    balance = client.balance.get_last_balance()
    print(f"Balance: {balance}")

if __name__ == "__main__":
    main()