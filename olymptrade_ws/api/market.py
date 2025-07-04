# api/market.py
import logging
import time
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Union
from datetime import datetime, timezone

from olymptrade_ws.core.protocol import get_current_timestamp_ms

if TYPE_CHECKING:
    from olymptrade_ws.core.client import OlympTradeClient

logger = logging.getLogger(__name__)

class MarketAPI:
    def __init__(self, client: 'OlympTradeClient'):
        self._client = client

    async def subscribe_ticks(self, pair: str) -> None:
        """Subscribes to live price ticks (Event 1) for a given asset pair."""
        logger.info(f"Subscribing to ticks for {pair}...")
        # Logs show events 12 and 280 are sent when subscribing to a pair
        try:
            # Event 12
            await self._client.send_request(12, [{"pair": pair}], requires_response=True)
             # Event 280
            await self._client.send_request(280, [{"pair": pair}], requires_response=True)
            logger.info(f"Successfully sent tick subscription requests for {pair}.")
        except Exception as e:
            logger.error(f"Failed to subscribe to ticks for {pair}: {e}")
            raise

    async def unsubscribe_ticks(self, pair: str) -> None:
        """Unsubscribes from live price ticks for a given asset pair."""
        logger.info(f"Unsubscribing from ticks for {pair}...")
         # Logs show events 13 and 281 are sent when unsubscribing
        try:
             # Event 13
            await self._client.send_request(13, [{"pair": pair}], requires_response=True)
            # Event 281
            await self._client.send_request(281, [{"pair": pair}], requires_response=True)
            logger.info(f"Successfully sent tick unsubscription requests for {pair}.")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from ticks for {pair}: {e}")
            raise
            
    async def get_candles(self, pair: str, size: int, count: int, end_time: Optional[Union[datetime, int]] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Requests historical candle data.

        Args:
            pair: Asset pair (e.g., "EURUSD", "ASIA_X").
            size: Candle size in seconds (e.g., 5, 60, 300).
            count: Number of candles to retrieve before end_time.
            end_time: Timestamp (int seconds or datetime object) for the *end* of the period.
                      Defaults to the current time.

        Returns:
            A list of candle dictionaries (format needs verification from e:1003 response) or None on error.
            
        NOTE: The exact mapping of 'count' to the API request ('solid'?) needs confirmation.
              The response format (event 1003) structure needs verification.
        """
        if end_time is None:
            to_ts = int(time.time())
        elif isinstance(end_time, datetime):
            # Ensure datetime is timezone-aware (assume UTC if naive)
            if end_time.tzinfo is None:
                 end_time = end_time.replace(tzinfo=timezone.utc)
            to_ts = int(end_time.timestamp())
        else:
            to_ts = int(end_time)

        logger.info(f"Requesting {count} candles for {pair} (size: {size}s) ending around {datetime.fromtimestamp(to_ts, tz=timezone.utc)}")
        
        # Event 10 seems to request candles, Event 1003 is the response in logs
        event_code_req = 10
        event_code_resp = 1003 # Expected response event code
        
        # The log shows 'solid: true'. This *might* relate to fetching historical batch?
        # The 'count' parameter isn't directly visible in the logged request payload.
        # The API might implicitly return a certain number based on 'to' and 'size',
        # or 'count' needs to be mapped differently (e.g., calculate 'from' timestamp).
        # Let's assume for now the API returns a batch ending at 'to'. We might need
        # multiple requests or a different parameter to get exactly 'count'.
        # For now, we request data ending at 'to_ts'.
        
        data = [{"pair": pair, "size": size, "to": to_ts, "solid": True}] # 'solid' is a guess
        
        # Also saw event 282 sent along with 10 in logs, purpose unclear. Send it too?
        event_code_req_alt = 282
        data_alt = [{"pair": pair, "size": size, "to": to_ts, "solid": True}]

        try:
            # Send the primary request (e:10) and expect a response (e:1003)
            # NOTE: The log for e:1003 doesn't show a UUID matching the e:10 request.
            # This suggests e:1003 might be an unsolicited push triggered by e:10,
            # or the UUID matching was missed in logging. Assuming direct response for now.
            response = await self._client.send_request(event_code_req, data, requires_response=True)
            
            # Optionally send the secondary request (e:282) if needed - requires_response=False?
            # await self._client.send_request(event_code_req_alt, data_alt, requires_response=False) 

            if response and response.get("e") == event_code_resp:
                 candles_data = response.get("d")
                 if isinstance(candles_data, list):
                     logger.info(f"Received {len(candles_data)} candles for {pair}.")
                     # TODO: Validate candle format [{p, t, open, low, high, close}, ...]
                     return candles_data
                 else:
                     logger.error(f"Unexpected data format in candle response: {candles_data}")
                     return None
            else:
                 logger.error(f"Did not receive expected candle response (e:{event_code_resp}). Got: {response}")
                 return None

        except Exception as e:
            logger.error(f"Failed to get candles for {pair}: {e}")
            return None

    async def get_profitability(self, account_id: int) -> Optional[List[Dict[str, Any]]]:
        """Requests current profitability for assets (Event 182)."""
        logger.info(f"Requesting asset profitability for account {account_id}...")
        event_code = 182
        data = [{"account_id": account_id}]
        try:
            response = await self._client.send_request(event_code, data, requires_response=True)
            if response and response.get("e") == event_code:
                profit_data = response.get("d")
                if isinstance(profit_data, list):
                    logger.info(f"Received profitability for {len(profit_data)} assets.")
                    return profit_data
                else:
                     logger.error(f"Unexpected data format in profitability response: {profit_data}")
                     return None
            else:
                logger.error(f"Did not receive expected profitability response (e:{event_code}). Got: {response}")
                return None
        except Exception as e:
            logger.error(f"Failed to get profitability: {e}")
            return None

    async def select_asset(self, pair: str, category: str = "digital") -> Optional[Dict[str, Any]]:
         """Selects an asset, potentially retrieving strike/payout info (Events 95, 80)."""
         logger.info(f"Selecting asset {pair} (category: {category})...")
         event_code_select = 95
         event_code_strikes = 80 # Often follows e:95 in logs
         data = [{"cat": category, "pair": pair}]
         try:
             # Send e:95 request
             response_select = await self._client.send_request(event_code_select, data, requires_response=True)
             if not (response_select and response_select.get("e") == event_code_select):
                 logger.error(f"Failed to get confirmation for asset selection (e:{event_code_select}).")
                 # Decide if we should proceed to wait for strikes anyway
             
             logger.info(f"Asset {pair} selected. Waiting for strike/payout info (e:{event_code_strikes})...")
             # Event 80 seems to be pushed after 95, not a direct response.
             # We need a way to wait for a specific *unsolicited* event.
             # Option 1: Register a temporary callback for e:80 with a filter for the pair.
             # Option 2: Have a general e:80 callback update internal state, then retrieve it.
             
             # Using Option 1 (temporary callback) for demonstration:
             future = asyncio.get_running_loop().create_future()

             async def temp_strike_callback(message: Dict[str, Any]):
                 strike_data_list = message.get("d", [])
                 if isinstance(strike_data_list, list):
                     for item in strike_data_list:
                         # Check if this strike data is for the requested pair
                         if isinstance(item, dict) and item.get("p") == pair:
                              if not future.done():
                                   future.set_result(item) # Return the specific strike data for the pair
                              break # Found our pair

             self._client.register_callback(event_code_strikes, temp_strike_callback)
             
             try:
                 # Wait for the callback to set the future's result
                 strike_info = await asyncio.wait_for(future, timeout=settings.DEFAULT_RESPONSE_TIMEOUT)
                 logger.info(f"Received strike info for {pair}: {strike_info}")
                 return strike_info
             except asyncio.TimeoutError:
                  logger.error(f"Timeout waiting for strike info (e:{event_code_strikes}) for {pair}.")
                  return None
             finally:
                  # Always unregister the temporary callback
                  self._client.unregister_callback(event_code_strikes, temp_strike_callback)

         except Exception as e:
             logger.error(f"Failed during asset selection/strike retrieval for {pair}: {e}")
             return None
