import sqlite3
from app.constants import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS ticker_data (
        ticker TEXT PRIMARY KEY,
        open REAL, high REAL, low REAL, close REAL, avg REAL,
        oi INTEGER, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS anomalies (
        type TEXT, open REAL, low REAL, high REAL, close REAL,
        threshold REAL, ticker TEXT, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS subscribed_symbols (
        symbol TEXT PRIMARY KEY,last_trade_price REAL

    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS anomalies_entry (
        stock TEXT, anomaly_type TEXT, market_open REAL, tpos TEXT, action TEXT,
        threshold_price REAL, status TEXT, current_price REAL,
        time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()
