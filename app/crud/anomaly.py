import sqlite3
from datetime import datetime
from app.constants import (
    STATUS_NO_BREAKOUT,
    ACTION_NO_BREAKOUT,
    DEFAULT_PRICE,
    DEFAULT_TIMEFRAME,
    TIME_FORMAT,
    ANOMALY_TICKERS
)
from app.constants import DB_PATH

#DB_PATH = "market_data.db"

# === Anomaly Ticker Functions ===
def get_anomaly_symbols():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker, type FROM anomaly_tickers")
    tickers = [{"ticker": row[0], "type": row[1]} for row in c.fetchall()]
    conn.close()
    return tickers


# def add_anomaly_symbol(symbol: str, type_: str = ""):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute(
#         "INSERT OR IGNORE INTO anomaly_tickers (ticker, type) VALUES (?, ?)",
#         (symbol.upper(), type_)
#     )
#     conn.commit()
#     conn.close()


def add_anomaly_symbol(symbol: str, type_: str = "Unknown"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Insert into anomaly_tickers table
    c.execute(
        "INSERT OR IGNORE INTO anomaly_tickers (ticker, type) VALUES (?, ?)",
        (symbol.upper(), type_)
    )

    # Insert into anomalies_entry table (ensure entry for today if not exists)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into anomalies_entry with the correct anomaly type
    c.execute('''
        INSERT INTO anomalies_entry (
            stock, anomaly_type, market_open, tpos, action, status, current_price, threshold_price, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
    symbol.upper(), type_.lower(), DEFAULT_PRICE, DEFAULT_TIMEFRAME, STATUS_NO_BREAKOUT, DEFAULT_PRICE, DEFAULT_PRICE, DEFAULT_PRICE, now))

    conn.commit()
    conn.close()
    print(f"Before Anomoly ticker insert : {ANOMALY_TICKERS}")
    # ✅ Reload shared anomaly ticker list
    ANOMALY_TICKERS.update(load_anomaly_tickers())
    print(f"After Anomoly ticker insert : {ANOMALY_TICKERS}")
    print(f"🟢 Inserted anomaly entry and added {symbol.upper()} with type {type_} to anomaly_tickers.")


def remove_anomaly_symbol(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM anomaly_tickers WHERE ticker = ?", (symbol.upper(),))
    # Delete all related entries in anomalies_entry
    c.execute("DELETE FROM anomalies_entry WHERE stock = ?", (symbol.upper(),))
    conn.commit()
    conn.close()



# === Anomaly Tickers Utilities ===
def load_anomaly_tickers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_tickers (
            ticker TEXT PRIMARY KEY,
            type TEXT DEFAULT ''
        )
    """)
    conn.commit()

    c.execute("SELECT * FROM anomaly_tickers")
    rows = c.fetchall()

    conn.close()

    return {row[0].upper(): row[1].lower() for row in rows}


# config.py (additional functions)
def insert_anomaly_entry(ticker, anomaly_type, market_open, tpos, action, threshold_price, price, current_time):
    import sqlite3
    print("I'm inside insert_anomaly_entry Function")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch the latest market_open value for the given ticker
    c.execute('''
        SELECT market_open FROM anomalies_entry
        WHERE stock = ?
        ORDER BY time DESC LIMIT 1
    ''', (ticker,))
    row = c.fetchone()
    previous_market_open = row[0] if row else market_open  # use previous if exists, else use provided

    c.execute('''
        INSERT INTO anomalies_entry (
            stock, anomaly_type, market_open, tpos, action, status, current_price, threshold_price, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticker, anomaly_type, previous_market_open, tpos, action, DEFAULT_PRICE, price, threshold_price, current_time))

    print("Data inserted anomaly type:", anomaly_type)
    conn.commit()
    conn.close()


def update_anomaly_action(ticker, action_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get the rowid of the latest entry where action is 'No Breakout'
    c.execute('''
        SELECT rowid FROM anomalies_entry
        WHERE stock = ? AND action = 'No Breakout'
        ORDER BY time DESC LIMIT 1
    ''', (ticker,))
    row = c.fetchone()

    if row:
        rowid = row[0]
        c.execute('''
            UPDATE anomalies_entry
            SET action = ?
            WHERE rowid = ?
        ''', (action_text, rowid))

    conn.commit()
    conn.close()


def update_anomaly_open_and_timeframe(ticker, open_price, timeframe, action):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE anomalies_entry
        SET market_open = ?, tpos = ?, action = ?
        WHERE stock = ? AND time = (SELECT MAX(time) FROM anomalies_entry WHERE stock = ?)
    ''', (open_price, timeframe, action, ticker, ticker))
    conn.commit()
    conn.close()




# config.py
def update_anomaly_status(ticker, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE anomalies_entry
        SET status = ?
        WHERE stock = ? AND time = (SELECT MAX(time) FROM anomalies_entry WHERE stock = ?)
    ''', (status, ticker, ticker))
    conn.commit()
    conn.close()


def get_all_anomaly_entries():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        SELECT ae.*
        FROM anomalies_entry ae
        JOIN anomaly_tickers at ON ae.stock = at.ticker
    ''')
    rows = c.fetchall()

    # Extract column names before closing the cursor
    columns = [desc[0] for desc in c.description]
    conn.close()

    result = [dict(zip(columns, row)) for row in rows]
    return result


def delete_anomaly_entries_by_stock(ticker):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        DELETE FROM anomalies_entry
        WHERE stock = ?
    ''', (ticker,))
    conn.commit()
    conn.close()
    print(f"Anomaly entries deleted for stock: {ticker}")
