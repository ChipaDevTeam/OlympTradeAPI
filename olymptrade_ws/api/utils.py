# api/utils.py
from datetime import datetime, timezone
from typing import Union

def ms_timestamp_to_datetime(ms_timestamp: Union[int, float]) -> datetime:
    """Converts a millisecond timestamp to a timezone-aware datetime object (UTC)."""
    return datetime.fromtimestamp(ms_timestamp / 1000, tz=timezone.utc)

def timestamp_to_datetime(ts: Union[int, float]) -> datetime:
     """Converts a second timestamp to a timezone-aware datetime object (UTC)."""
     return datetime.fromtimestamp(ts, tz=timezone.utc)

# Add other utility functions as needed (e.g., parsing specific data structures)
