import sqlite3
from datetime import datetime
from app.constants import (
    STATUS_NO_BREAKOUT,
    ACTION_NO_BREAKOUT,
    DEFAULT_PRICE,
    DEFAULT_TIMEFRAME,
    TIME_FORMAT,
)
from app.constants import DB_PATH



# === Subscribe Symbol Functions ===
def get_subscribe_symbols():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT symbol FROM subscribed_symbols")
    symbols = [row[0] for row in c.fetchall()]
    conn.close()
    return symbols

def add_subscribe_symbol(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribed_symbols (symbol) VALUES (?)", (symbol.upper(),))
    conn.commit()
    conn.close()

def remove_subscribe_symbol(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM subscribed_symbols WHERE symbol = ?", (symbol.upper(),))
    conn.commit()
    conn.close()
