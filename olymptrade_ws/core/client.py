# core/client.py
import asyncio
import logging
from typing import Any, Dict, Optional, Callable, Awaitable, List, Coroutine
from collections import defaultdict
# core/client.py - Line 6 (Corrected)
from olymptrade_ws.olympconfig import parameters
from .connection import Connection
from .protocol import format_message, parse_message, generate_uuid
from olymptrade_ws.api import balance, market, trade # Import API modules
import olymptrade_ws.olympconfig.parameters as settings

logger = logging.getLogger(__name__)

class OlympTradeClient:
    def __init__(self, access_token: str, uri: str = parameters.DEFAULT_WEBSOCKET_URI, log_raw_messages: bool = False, account_id: int = None, account_group: str = None):
        logger.info(f"Initializing OlympTradeClient with uri={uri}, log_raw_messages={log_raw_messages}, account_id={account_id}, account_group={account_group}")
        self.access_token = access_token
        self.uri = uri
        self.account_id = account_id
        self.account_group = account_group
        self.message_queue = asyncio.Queue()
        self.connection = Connection(self.uri, self.access_token, self.message_queue, self._connection_lost_handler)
        
        self._response_futures: Dict[str, asyncio.Future] = {}
        self._event_callbacks: Dict[int, List[Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]]] = defaultdict(list)
        self._is_running = False
        self._processing_task: Optional[asyncio.Task] = None
        self._ping_task: Optional[asyncio.Task] = None
        self._log_raw_messages = log_raw_messages
        self._raw_log_file = "logs/message_logbook.md" # Consider making configurable

        # --- API Modules ---
        self.balance = balance.BalanceAPI(self)
        self.market = market.MarketAPI(self)
        self.trade = trade.TradeAPI(self)
        # Add other API modules here

        # --- Internal State ---
        self._latest_balance: Dict[str, Any] = {} # Store latest balance update (e:55)
        self.account_id = None
        self.account_group = None # To store the account group (demo/real)


    async def start(self):
        logger.info("Starting OlympTradeClient...")
        if self._is_running:
            logger.warning("Client is already running.")
            return
        
        try:
            await self.connection.connect()
            self._is_running = True
            self._processing_task = asyncio.create_task(self._process_messages())
            self._ping_task = asyncio.create_task(self._ping_loop())
            logger.info("Client started successfully.")
        except ConnectionError as e:
            logger.error(f"Client failed to start: {e}")
            self._is_running = False
            # Optionally re-raise or handle startup failure
            raise

    async def stop(self):
        logger.info("Stopping OlympTradeClient...")
        if not self._is_running:
            logger.warning("Client is not running.")
            return
            
        self._is_running = False # Signal loops to stop
        
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            
        await self.connection.disconnect()

        # Wait for tasks to finish cancellation
        try:
            if self._ping_task: await self._ping_task
        except asyncio.CancelledError: pass
        try:
             if self._processing_task: await self._processing_task
        except asyncio.CancelledError: pass
        
        logger.info("Client stopped.")
        # Clean up any pending futures
        for fut in self._response_futures.values():
            if not fut.done():
                fut.cancel("Client stopping")
        self._response_futures.clear()


    async def _connection_lost_handler(self):
        """Callback executed by Connection when the websocket closes unexpectedly."""
        logger.warning("Connection lost. Attempting to clean up and stop client.")
        # Signal loops to stop if they haven't already noticed
        self._is_running = False 
        if self._ping_task and not self._ping_task.done():
            self._ping_task.cancel()
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            
        # Clean up pending futures with an error
        for fut in self._response_futures.values():
            if not fut.done():
                fut.set_exception(ConnectionError("WebSocket connection lost"))
        self._response_futures.clear()
        
        # TODO: Implement reconnection logic here if desired
        logger.info("Client state reset due to connection loss. Manual restart required (or implement auto-reconnect).")


    def register_callback(self, event_code: int, callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]):
        logger.info(f"Registering callback for event_code={event_code}, callback={callback}")
        """Register a callback for a specific unsolicited event code (e.g., ticks, balance updates)."""
        self._event_callbacks[event_code].append(callback)

    def unregister_callback(self, event_code: int, callback: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]]):
        logger.info(f"Unregistering callback for event_code={event_code}, callback={callback}")
        """Unregister a specific callback."""
        if event_code in self._event_callbacks:
            try:
                self._event_callbacks[event_code].remove(callback)
                if not self._event_callbacks[event_code]: # Remove key if list is empty
                    del self._event_callbacks[event_code]
            except ValueError:
                logger.warning(f"Callback not found for event code {event_code}")


    async def send_request(self, event_code: int, data: Any, requires_response: bool = True, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        #logger.info(f"send_request called with event_code={event_code}, data={data}, requires_response={requires_response}, timeout={timeout}")
        """
        Sends a request to the WebSocket server and optionally waits for a response.
        
        Args:
            event_code: The integer event code for the request.
            data: The data payload for the request (usually a list of dicts).
            requires_response: If True, waits for a response matched by UUID.
            timeout: Custom timeout for waiting for the response. Uses default if None.

        Returns:
            The parsed response dictionary if requires_response is True, otherwise None.
            
        Raises:
            ConnectionError: If the WebSocket is not connected.
            asyncio.TimeoutError: If waiting for a response times out.
            Exception: For other send/serialization errors.
        """
        if not self.connection.is_connected:
            logger.error("Cannot send request: Not connected.")
            raise ConnectionError("Not connected")

        request_uuid = generate_uuid() if requires_response else None
        message_str = format_message(event_code, data, request_uuid)
        
        logger.debug(f"📤 Sending (e:{event_code}, uuid:{request_uuid}): {data}")
        if self._log_raw_messages:
             self._log_raw("📤 SENT", message_str)

        future = None
        if requires_response and request_uuid:
            future = asyncio.get_running_loop().create_future()
            self._response_futures[request_uuid] = future

        try:
            await self.connection.send(message_str)
        except Exception as e:
            # Clean up future if send fails
            if request_uuid in self._response_futures:
                del self._response_futures[request_uuid]
                if future and not future.done():
                     future.set_exception(e) # Propagate send error
            raise # Re-raise the sending error

        if future:
            try:
                response_timeout = timeout if timeout is not None else parameters.DEFAULT_RESPONSE_TIMEOUT
                result = await asyncio.wait_for(future, timeout=response_timeout)
                return result
            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for response to request uuid {request_uuid} (e:{event_code})")
                # Remove future on timeout
                if request_uuid in self._response_futures:
                     del self._response_futures[request_uuid]
                raise
            except asyncio.CancelledError:
                 logger.warning(f"Request uuid {request_uuid} (e:{event_code}) cancelled.")
                 # Future might already be removed if cancelled via stop()
                 if request_uuid in self._response_futures:
                      del self._response_futures[request_uuid]
                 raise
        else:
            return None # No response expected


    async def _process_messages(self):
        logger.info("_process_messages loop started.")
        """Continuously processes messages from the connection queue."""
        while self._is_running:
            try:
                raw_message = await self.message_queue.get()
                if self._log_raw_messages:
                     self._log_raw("📥 RECEIVED", raw_message)
                     
                parsed_messages = parse_message(raw_message)
                if not parsed_messages:
                    continue # Skip invalid messages

                for message in parsed_messages:
                    await self._dispatch_message(message)

            except asyncio.CancelledError:
                 logger.info("Message processing loop cancelled.")
                 break
            except Exception as e:
                logger.exception(f"Error processing message queue: {e}")
                # Avoid breaking the loop on unexpected errors, maybe add delay
                await asyncio.sleep(1)
        logger.info("Message processing loop finished.")

    async def _dispatch_message(self, message: Dict[str, Any]):
        logger.info(f"_dispatch_message called with message: {message}")
        """Handles a single parsed message dictionary."""
        request_uuid = message.get("uuid")
        event_code = message.get("e")
        message_type = message.get("t") # 1: Server Push, 3: Response/Push?

        if not event_code:
            logger.warning(f"Received message without event code: {message}")
            return

        # --- Handle Responses to Requests ---
        if request_uuid and request_uuid in self._response_futures:
            future = self._response_futures.pop(request_uuid)
            if not future.done():
                logger.debug(f"Received response for uuid {request_uuid} (e:{event_code})")
                future.set_result(message)
            else:
                 logger.warning(f"Received response for already completed/cancelled uuid {request_uuid}")
            # Even if it was a response, it might *also* be an event we have callbacks for
            # Fall through to check callbacks unless we are sure responses are never also events.
            # Based on logs (e.g., e:23 response AND e:22 push), it seems responses can be separate from pushes.
            # Let's assume a message with a matched UUID is *only* a response for now.
            return # Don't process as a general event if it was a direct response

        # --- Handle Internal State Updates ---
        if event_code == settings.E_BALANCE_UPDATE:
            logger.debug(f"Received balance update (e:{event_code}): {message.get('d')}")
            # Store the latest balance data (assuming 'd' contains the relevant list/dict)
            # The log shows 'd' is a list of account dicts. Find the relevant one if needed.
            self._latest_balance = message # Store the whole message for now
        
        # --- Handle Registered Callbacks for Unsolicited Events ---
        if event_code in self._event_callbacks:
            logger.debug(f"Dispatching event {event_code} to {len(self._event_callbacks[event_code])} callbacks.")
            # Create tasks for each callback to avoid blocking the dispatcher
            callback_tasks = [
                asyncio.create_task(cb(message)) 
                for cb in self._event_callbacks[event_code]
            ]
            # Optionally gather results or just let them run
            # asyncio.gather(*callback_tasks) # If you need to wait/handle errors
        else:
             # Log unhandled events if needed (can be noisy)
             # logger.debug(f"Received unhandled event (e:{event_code}): {message}")
             pass


    async def _ping_loop(self):
        logger.info("_ping_loop started.")
        """Sends periodic pings (e.g., event 90) to keep the connection alive."""
        while self._is_running:
            try:
                await asyncio.sleep(parameters.PING_INTERVAL)
                if not self.connection.is_connected:
                    logger.warning("Ping loop: Not connected, skipping ping.")
                    continue
                
                logger.debug("Sending ping...")
                # Event 90 seems to be the ping/keep-alive based on logs
                # It requires a UUID and returns a timestamp
                try:
                    # Send ping and wait for response to ensure connection is active
                    response = await self.send_request(settings.E_PING, {}, requires_response=True, timeout=5) 
                    if response:
                         logger.debug(f"Pong received (ts: {response.get('ts')})")
                    else:
                         logger.warning("Did not receive pong response within timeout.")
                         # Consider triggering connection check/reconnect here
                except ConnectionError:
                     logger.warning("Ping failed: Connection error.")
                     # Connection loss is handled by the receiver loop / callback
                except asyncio.TimeoutError:
                     logger.warning("Ping failed: Timeout waiting for pong.")
                     # Consider triggering connection check/reconnect here
                except Exception as e:
                     logger.error(f"Error during ping: {e}")

            except asyncio.CancelledError:
                logger.info("Ping loop cancelled.")
                break
            except Exception as e:
                 logger.exception(f"Unexpected error in ping loop: {e}")
                 await asyncio.sleep(settings.PING_INTERVAL) # Avoid tight loop on error

    def _log_raw(self, direction: str, message: str):
        logger.debug(f"_log_raw called with direction={direction}, message={message}")
        """Logs raw messages to the markdown file. Ensures logs directory exists."""
        import os
        log_dir = os.path.dirname(self._raw_log_file)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create log directory: {e}")
                return
        try:
            with open(self._raw_log_file, "a") as f:
                f.write(f"```json\n{direction} ➜ {message}\n```\n")
        except Exception as e:
            logger.error(f"Failed to write to raw log file: {e}")
    # --- Convenience property to get last known balance ---
    @property
    def current_balance(self) -> Dict[str, Any]:
        """Returns the last known balance dictionary received from the server (event 55)."""
        return self._latest_balance

    async def initialize_session(self):
        """
        Sends the required subscription, ping, and account info requests after connecting.
        This mimics the browser's startup sequence.
        """
        logger.info("Sending initial subscription, ping, and account info requests...")
        # 1. Send e:98 subscriptions (mimic browser)
        startup_subscriptions = [
            [220],
            [110,700,112,140,1038,1037,1039,141,22,26,111],
            [1054,1076,1301,1097],
            [141,241],
            [230,231],
            [75],
            [1055],
            [2223,2301,55,150,152,151,126,602,601],
            [2076],
            [126],
        ]
        for sub in startup_subscriptions:
            await self.send_request(98, sub, requires_response=False)
        # 2. Send initial pings (e:90) - not strictly required, but mimics browser
        import uuid
        for _ in range(2):
            await self.send_request(90, {}, requires_response=True)  # uuid auto-generated
        # 3. Request account info (demo and real)
        self.account_id = self.account_id or None
        self.account_group = self.account_group or None
        for group in ["demo", "real"]:
            try:
                resp = await self.send_request(1068, [{"group": group}], requires_response=True)
                logger.info(f"Account info response for group {group}: {resp}")
                if resp and 'd' in resp and isinstance(resp['d'], list) and resp['d']:
                    self.account_id = resp['d'][0].get('account_id')
                    self.account_group = group
                    logger.info(f"Set account_id to {self.account_id} (group: {group})")
                    break
            except Exception as e:
                logger.warning(f"Failed to get account_id for group {group}: {e}")
        if not self.account_id:
            logger.error("Could not determine account_id from account info requests.")
        # 4. Request balance for the found account_id
        if self.account_id:
            try:
                resp = await self.send_request(1043, [{"account_id": self.account_id, "group": self.account_group}], requires_response=True)
                logger.info(f"Balance info response: {resp}")
            except Exception as e:
                logger.warning(f"Failed to get balance for account_id {self.account_id}: {e}")

    async def wait_for_balance(self, timeout: float = 10.0, poll_interval: float = 0.5):
        """
        Waits until a balance update is received or timeout is reached.
        Returns the balance dict if received, else None.
        """
        logger.info(f"Waiting for balance update (timeout={timeout}s)...")
        waited = 0.0
        while waited < timeout:
            balance = self.balance.get_last_balance()
            if balance and 'd' in balance and balance['d']:
                logger.info("Balance update received.")
                return balance
            await asyncio.sleep(poll_interval)
            waited += poll_interval
        logger.warning("Timeout waiting for balance update.")
        return None
