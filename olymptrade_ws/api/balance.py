# api/balance.py
import logging
from typing import TYPE_CHECKING, Dict, Any, Optional

if TYPE_CHECKING:
    from core.client import OlympTradeClient # Avoid circular import

logger = logging.getLogger(__name__)

class BalanceAPI:
    def __init__(self, client: 'OlympTradeClient'):
        self._client = client

    async def subscribe_balance_updates(self) -> None:
        """
        Subscribes to real-time balance updates (Event 55).
        The actual balance data will be delivered via registered callbacks for event 55.
        NOTE: The exact subscription mechanism (e.g., using event 98) needs confirmation from logs.
              This is based on the assumption that subscribing to event 55 via event 98 works.
        """
        event_code_subscribe = 98 # GUESS based on logs pattern
        event_code_balance = 55
        
        # Assuming event 98 subscribes to other events listed in its data array
        # This needs verification by observing network traffic when balance updates start.
        # The specific list [55, 150, ...] might subscribe to multiple things at once.
        # Let's try subscribing only to 55 for clarity.
        data = [event_code_balance] 
        
        logger.info(f"Attempting to subscribe to balance updates (event {event_code_balance}) using event {event_code_subscribe}...")
        try:
            # Subscription does not require a response; server sends updates unsolicited
            await self._client.send_request(event_code_subscribe, [data], requires_response=False)
            logger.info(f"Subscription request for balance updates sent.")
        except Exception as e:
             logger.error(f"Failed to send subscription request for balance updates: {e}")
             raise

    def get_last_balance(self) -> Dict[str, Any]:
        """
        Returns the most recently received balance information.
        Requires balance updates to be subscribed and received first.
        """
        balance_data = self._client.current_balance
        if not balance_data:
             logger.warning("No balance data received yet. Ensure you are subscribed and connected.")
        return balance_data
        
    async def request_balance(self, account_id: int, group: str = "real") -> Optional[Dict[str, Any]]:
        """
        Explicitly requests current balance state (if possible).
        NOTE: The exact mechanism (event code, data) is UNCLEAR from the logs.
              Events 1068/1043 seem related to account state but return empty 'd' in logs.
              This function might not work as expected without further API reverse-engineering.
              It might be better to rely on subscribing (subscribe_balance_updates) and
              using get_last_balance() or callbacks.
        """
        logger.warning("Explicitly requesting balance is currently speculative based on logs.")
        # Try event 1068 as a guess
        event_code = 1068 # GUESS!
        data = [{"account_id": account_id, "group": group}]
        try:
            response = await self._client.send_request(event_code, data, requires_response=True)
            logger.info(f"Received response for balance request (e:{event_code}): {response}")
            # Parse response - structure unknown, logs show empty 'd' for this event's response
            return response # Return raw response for inspection
        except Exception as e:
            logger.error(f"Failed to request balance using event {event_code}: {e}")
            return None

    async def get_balance(self, timeout: float = 10.0, poll_interval: float = 0.5) -> dict:
        """
        Ensures session initialization, subscribes, and waits for a balance update, then returns it.
        Usage: balance = await client.balance.get_balance()
        """
        # Ensure all startup subscriptions and account_id are set
        if not getattr(self._client, '_session_initialized', False):
            await self._client.initialize_session()
            self._client._session_initialized = True
        try:
            await self.subscribe_balance_updates()
        except Exception:
            pass  # Ignore if already subscribed or fails
        balance = await self._client.wait_for_balance(timeout=timeout, poll_interval=poll_interval)
        return balance
