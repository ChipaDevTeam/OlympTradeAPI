# config/settings.py

# Default WebSocket URI (consider making this configurable)
DEFAULT_WEBSOCKET_URI = "wss://ws.olymptrade.com/otp?cid_ver=1&cid_app=web%40OlympTrade%402025.2.26123%4026123&cid_device=%40%40desktop&cid_os=windows%4010"

# Default Headers
DEFAULT_ORIGIN = "https://olymptrade.com"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"

# Timeouts (in seconds)
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_RESPONSE_TIMEOUT = 15
PING_INTERVAL = 25 # Interval to send keep-alive pings (e.g., e:90)

# Logging configuration
LOG_LEVEL = "INFO" # e.g., DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Event Codes (Inferred from logs - NEEDS VERIFICATION AND COMPLETION)
# Naming convention: E_<Description>
E_TICK_UPDATE = 1
E_GET_CANDLES_RESPONSE = 1003
E_GET_CANDLES_REQUEST = 10
E_SUBSCRIBE_CANDLES = 282 # Associated with candles?
E_UNSUBSCRIBE_CANDLES = 281 # Associated with candles?
E_CANDLE_TIME_UPDATE = 11
E_CANDLE_VOLUME_UPDATE = 283 # Associated with candles?

E_SUBSCRIBE_TICKS = 12
E_UNSUBSCRIBE_TICKS = 13
E_SUBSCRIBE_TICKS_RELATED = 280 # Also seems needed for ticks?
E_UNSUBSCRIBE_TICKS_RELATED = 281 # Also seems needed for ticks?

E_PLACE_TRADE_REQUEST = 23
E_TRADE_UPDATE_INTERIM = 21 # Interim win/loss status
E_TRADE_ACCEPTED = 22       # Trade placed successfully
E_TRADE_CLOSED = 26         # Final trade result

E_BALANCE_UPDATE = 55
E_GET_BALANCE_REQUEST_1 = 1068 # Possibly related? Needs confirmation
E_GET_BALANCE_REQUEST_2 = 1043 # Possibly related? Needs confirmation

E_ASSET_PROFITABILITY = 182
E_ASSET_PROFITABILITY_UPDATE = 183

E_ASSET_STRIKES = 80
E_SELECT_ASSET = 95

E_PING = 90
E_SUBSCRIBE_EVENTS = 98 # Generic subscription mechanism?

E_SENTIMENT_UPDATE = 73
E_USER_INFO = 110 # Contains email confirmed status etc.
E_OPEN_TRADES_REQUEST = 31 # Needs confirmation

# Add other identified event codes here...
