# core/protocol.py
import uuid
import json
import time
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

def generate_uuid() -> str:
    """Generates a unique request identifier."""
    # OlympTrade seems to use a specific format, let's mimic based on logs
    # Example: M99KQLV7C1IV4OSU8U - This looks like base36 or similar, not standard UUID
    # Using standard UUID for now, might need adjustment if format is strict
    # Update: Let's try a simpler random string based on logs like 'k7YAyt'
    import random
    import string
    # return str(uuid.uuid4())
    prefix = random.choice(string.ascii_uppercase) + \
             random.choice(string.ascii_uppercase) + \
             random.choice(string.ascii_uppercase) + \
             random.choice(string.ascii_uppercase)
    suffix = random.choice(string.ascii_lowercase) + \
             random.choice(string.ascii_lowercase)
    return f"{prefix}-{suffix}" # Example: ABCD-xy - Adjust length/chars as needed

def format_message(event_code: int, data: Any, request_uuid: Optional[str] = None) -> str:
    """Formats a message payload for sending."""
    message_part = {
        "t": 2, # Type 2 for client requests
        "e": event_code,
        "d": data
    }
    if request_uuid:
        message_part["uuid"] = request_uuid
    
    # Messages seem to be lists containing one or more dictionaries
    message_list = [message_part]
    
    # Handle cases where multiple messages are sent together (seen in logs)
    # This needs more clarity - for now, assume one message per call
    
    try:
        return json.dumps(message_list)
    except TypeError as e:
        logger.error(f"Failed to serialize message data: {data} for event {event_code}. Error: {e}")
        raise

def parse_message(raw_message: str) -> Optional[List[Dict[str, Any]]]:
    """Parses a received raw message string."""
    try:
        data = json.loads(raw_message)
        if isinstance(data, list):
            return data
        else:
            logger.warning(f"Received non-list message format: {raw_message}")
            return None
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON message: {raw_message}")
        return None
    except Exception as e:
        logger.error(f"Error parsing message: {raw_message}. Error: {e}")
        return None

def get_current_timestamp_ms() -> int:
    """Gets the current time as milliseconds since epoch."""
    return int(time.time() * 1000)
