# main.py
import asyncio
import logging
import os
import signal
from typing import Dict, Any # Added for type hinting
from olympconfig import parameters

# Imports assuming main.py is run from the olymptrade_ws directory
from core.client import OlympTradeClient
# core/client.py - Line 6 (Corrected)
from api.utils import timestamp_to_datetime

# --- Configuration ---
logging.basicConfig(level=parameters.LOG_LEVEL, format=parameters.LOG_FORMAT)
logger = logging.getLogger(__name__)

# --- Global variable to store results if needed (or use a class) ---
# This is a simple way for the callback to share data with the main flow
# A more robust solution might involve passing a shared state object or using queues.
trade_results: Dict[int, Dict[str, Any]] = {} # Store results keyed by trade ID

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
                 # logger.info(f"TICK >> Pair: {pair}, Price: {price}, Time: {dt.strftime('%H:%M:%S.%f')[:-3]}")
                 # Keep logging minimal for clarity unless debugging ticks
                 pass

async def on_balance_update(message: dict):
    """Callback for processing balance updates (Event 55)."""
    balance_data_list = message.get("d", [])
    logger.info(f"BALANCE UPDATE >> {balance_data_list}")
    # You could update external state or trigger other logic here

async def on_trade_update(message: dict):
    """Callback for processing trade updates (Events 21, 22, 26)."""
    global trade_results # Allow modifying the global dictionary

    event_code = message.get("e")
    trade_data_list = message.get("d", [])
    if isinstance(trade_data_list, list) and len(trade_data_list) > 0:
        trade_info = trade_data_list[0]
        trade_id = trade_info.get("id")

        if not trade_id:
            logger.warning(f"Received trade update without ID (e:{event_code}): {trade_info}")
            return

        status = trade_info.get("status")
        interim_status = trade_info.get("interim_status")

        if event_code == settings.E_TRADE_ACCEPTED: # 22
             logger.info(f"TRADE ACCEPTED >> ID: {trade_id}, Status: {status}")
             # Store initial info if needed
             trade_results[trade_id] = {"status": status, "accepted_data": trade_info}
        elif event_code == settings.E_TRADE_UPDATE_INTERIM: # 21
             # logger.info(f"TRADE INTERIM >> ID: {trade_id}, Status: {interim_status}, PnL: {trade_info.get('interim_balance_change')}")
             # Update existing record
             if trade_id in trade_results:
                 trade_results[trade_id]["interim_status"] = interim_status
                 trade_results[trade_id]["interim_pnl"] = trade_info.get('interim_balance_change')
                 trade_results[trade_id]["last_update_time"] = timestamp_to_datetime(time.time())
             else:
                 logger.warning(f"Received interim update for unknown trade ID: {trade_id}")
        elif event_code == settings.E_TRADE_CLOSED: # 26
             pnl = trade_info.get('balance_change')
             close_price = trade_info.get('curs_close')
             logger.info(f"TRADE CLOSED >> ID: {trade_id}, Status: {status}, PnL: {pnl}, ClosePrice: {close_price}")
             # Store the final result
             trade_results[trade_id] = {"status": status, "pnl": pnl, "closed_data": trade_info}
             # Optionally notify another part of your application that this trade is done
             # e.g., by setting an asyncio.Event if you were waiting specifically for this ID.
        else:
             logger.warning(f"Unhandled trade event {event_code}: {trade_info}")

async def run_client():
    """Main function to run the client."""

    # Ensure logs directory exists
    if not os.path.exists("logs"):
        try:
            os.makedirs("logs")
        except OSError as e:
            logger.error(f"Could not create logs directory: {e}")
            # Decide if you want to continue without logging raw messages

    token = input("🔐 Enter your OlympTrade access_token: ").strip()
    if not token:
        logger.error("Access token is required.")
        return

    # Enable raw logging to help debug if needed
    client = OlympTradeClient(access_token=token, log_raw_messages=True)

    # --- Register Callbacks ---
    client.register_callback(parameters.E_TICK_UPDATE, on_tick)
    client.register_callback(parameters.E_BALANCE_UPDATE, on_balance_update)
    # Register the single handler for all relevant trade events
    client.register_callback(parameters.E_TRADE_ACCEPTED, on_trade_update)
    client.register_callback(parameters.E_TRADE_UPDATE_INTERIM, on_trade_update)
    client.register_callback(parameters.E_TRADE_CLOSED, on_trade_update)
    # Register callbacks for other events as needed (e.g., profitability updates E_ASSET_PROFITABILITY_UPDATE)

    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("Stop signal received, shutting down...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    # Add signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
         # Use try-except for environments where add_signal_handler might not be available (e.g., some Windows setups)
         try:
            loop.add_signal_handler(sig, signal_handler)
         except NotImplementedError:
             logger.warning(f"Signal handler for {sig} not supported on this platform.")


    try:
        await client.start()
        logger.info("Client started. Press Ctrl+C to stop.")

        # --- Example API Calls ---
        try:
            # Subscribe to balance updates (mechanism needs verification)
            await client.balance.subscribe_balance_updates()
            await asyncio.sleep(2) # Give time for initial balance push

            # Get last known balance to find account ID
            current_bal_msg = client.balance.get_last_balance()
            logger.info(f"Initial Balance Info Message: {current_bal_msg}")

            demo_account_id = None
            if current_bal_msg and 'd' in current_bal_msg and isinstance(current_bal_msg['d'], list):
                 for acc in current_bal_msg['d']:
                     if acc.get('group') == 'demo':
                         demo_account_id = acc.get('account_id')
                         logger.info(f"Found Demo Account ID: {demo_account_id}")
                         break

            if not demo_account_id:
                 logger.error("Could not determine demo account ID from balance update. Cannot place demo trade.")
                 # Optionally try a hardcoded ID or stop
                 # demo_account_id = 2860109309 # From your logs - USE WITH CAUTION

            # Subscribe to ticks for a specific pair
            pair_to_watch = "EURUSD" # Change as needed
            await client.market.subscribe_ticks(pair_to_watch)

            # Example: Place a demo trade
            placed_trade_id = None
            if demo_account_id:
                 logger.info("Attempting to place a demo trade...")
                 trade_duration_seconds = 60 # Example: 1 minute trade
                 trade_amount = 1 # Example amount

                 initial_response = await client.trade.place_trade(
                     pair=pair_to_watch,
                     amount=trade_amount,
                     direction="up", # Or "down"
                     duration=trade_duration_seconds,
                     account_id=demo_account_id,
                     group="demo"
                 )

                 if initial_response and initial_response.get("id"):
                      placed_trade_id = initial_response.get("id")
                      logger.info(f"Demo trade placed, ID: {placed_trade_id}. Waiting for result via callback...")
                 else:
                      logger.error(f"Demo trade placement failed or did not return an ID. Response: {initial_response}")
            else:
                 logger.warning("Cannot place demo trade, demo account ID unknown.")

            # --- Wait for the trade result (or timeout/shutdown) ---
            # The result will arrive asynchronously and be handled by `on_trade_update`
            # We just keep the client running here.
            logger.info("Client running, waiting for events or stop signal...")
            await stop_event.wait() # Wait indefinitely until Ctrl+C or SIGTERM

            # --- After stopping, check the result (if the trade completed) ---
            if placed_trade_id and placed_trade_id in trade_results:
                final_result = trade_results[placed_trade_id]
                logger.info(f"Final result for trade {placed_trade_id}: {final_result}")
            elif placed_trade_id:
                logger.warning(f"Trade {placed_trade_id} was placed, but no final result received before shutdown.")


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
