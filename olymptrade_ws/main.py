# main.py
import asyncio
import logging
import os
import signal
from core.client import OlympTradeClient
from config import settings # Import event codes
from api.utils import timestamp_to_datetime

# --- Configuration ---
logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

# --- Callback Functions ---
async def on_tick(message: dict):
    """Callback for processing tick updates (Event 1)."""
    tick_data_list = message.get("d", [])
    if isinstance(tick_data_list, list):
        for tick in tick_data_list:
             pair = tick.get("p")
             price = tick.get("q")
             ts = tick.get("t")
             if pair and price and ts:
                 dt = timestamp_to_datetime(ts)
                 logger.info(f"TICK >> Pair: {pair}, Price: {price}, Time: {dt.strftime('%H:%M:%S.%f')[:-3]}")

async def on_balance_update(message: dict):
    """Callback for processing balance updates (Event 55)."""
    balance_data_list = message.get("d", [])
    logger.info(f"BALANCE UPDATE >> {balance_data_list}")
    # You could update external state or trigger other logic here

async def on_trade_update(message: dict):
    """Callback for processing trade updates (Events 21, 22, 26)."""
    event_code = message.get("e")
    trade_data_list = message.get("d", [])
    if isinstance(trade_data_list, list) and len(trade_data_list) > 0:
        trade_info = trade_data_list[0]
        trade_id = trade_info.get("id")
        status = trade_info.get("status")
        interim_status = trade_info.get("interim_status")
        
        if event_code == settings.E_TRADE_ACCEPTED: # 22
             logger.info(f"TRADE ACCEPTED >> ID: {trade_id}, Status: {status}")
        elif event_code == settings.E_TRADE_UPDATE_INTERIM: # 21
             logger.info(f"TRADE INTERIM >> ID: {trade_id}, Status: {interim_status}, PnL: {trade_info.get('interim_balance_change')}")
        elif event_code == settings.E_TRADE_CLOSED: # 26
             logger.info(f"TRADE CLOSED >> ID: {trade_id}, Status: {status}, PnL: {trade_info.get('balance_change')}, ClosePrice: {trade_info.get('curs_close')}")
        else:
             logger.warning(f"Unhandled trade event {event_code}: {trade_info}")

async def run_client():
    """Main function to run the client."""
    
    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    token = input("🔐 Enter your OlympTrade access_token: ").strip()
    if not token:
        logger.error("Access token is required.")
        return

    client = OlympTradeClient(access_token=token, log_raw_messages=True) # Enable raw logging

    # --- Register Callbacks ---
    client.register_callback(settings.E_TICK_UPDATE, on_tick)
    client.register_callback(settings.E_BALANCE_UPDATE, on_balance_update)
    client.register_callback(settings.E_TRADE_ACCEPTED, on_trade_update)
    client.register_callback(settings.E_TRADE_UPDATE_INTERIM, on_trade_update)
    client.register_callback(settings.E_TRADE_CLOSED, on_trade_update)
    # Register callbacks for other events as needed

    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Stop signal received, shutting down...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
         loop.add_signal_handler(sig, signal_handler)

    try:
        await client.start()
        logger.info("Client started. Press Ctrl+C to stop.")

        # --- Example API Calls ---
        try:
            # Subscribe to balance updates (mechanism needs verification)
            await client.balance.subscribe_balance_updates()
            await asyncio.sleep(2) # Give time for initial balance push

            # Get last known balance
            current_bal = client.balance.get_last_balance()
            logger.info(f"Initial Balance Info: {current_bal}")

            # Subscribe to ticks for a specific pair
            pair_to_watch = "EURUSD" # Change as needed
            await client.market.subscribe_ticks(pair_to_watch)
            
            # Get profitability
            # Need account ID - assuming it's in the balance info
            demo_account_id = None
            if current_bal and 'd' in current_bal and isinstance(current_bal['d'], list):
                 for acc in current_bal['d']:
                     if acc.get('group') == 'demo':
                         demo_account_id = acc.get('account_id')
                         break
            
            if demo_account_id:
                 profitability = await client.market.get_profitability(demo_account_id)
                 # logger.info(f"Profitability: {profitability}")
            else:
                 logger.warning("Could not determine demo account ID to fetch profitability.")


            # Example: Place a demo trade after a delay
            await asyncio.sleep(10) 
            if demo_account_id:
                 logger.info("Attempting to place a demo trade...")
                 trade_result = await client.trade.place_trade(
                     pair=pair_to_watch,
                     amount=1, # Example amount
                     direction="up",
                     duration=60, # Example duration (needs confirmation if seconds)
                     account_id=demo_account_id,
                     group="demo"
                 )
                 if trade_result:
                      logger.info(f"Demo trade placed, initial response: {trade_result}")
                 else:
                      logger.error("Demo trade placement failed.")
            else:
                 logger.warning("Cannot place demo trade, demo account ID unknown.")

            # Keep running until stop signal
            await stop_event.wait()

        except ConnectionError:
             logger.error("Connection error during API calls. Client might have stopped.")
        except Exception as e:
            logger.exception(f"An error occurred during client operation: {e}")

    finally:
        logger.info("Cleaning up...")
        await client.stop()
        logger.info("Client shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received.")
