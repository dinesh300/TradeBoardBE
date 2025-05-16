# app/constants.py
DEFAULT_PRICE = 0.0
DEFAULT_TIMEFRAME = "-"

# Database name
DB_PATH = "market_data_live.db"

# app/globals.py
ANOMALY_TICKERS = {}


# Statuses
STATUS_NO_BREAKOUT = "no_breakout"
STATUS_BREAKOUT = "-"

# Actions
ACTION_NO_BREAKOUT = "No Breakout"
ACTION_BREAKOUT = "Breakout"

# Default Values
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# WS Message Types
WS_MSG_TYPE_THRESHOLD_UPDATE = "threshold_update"