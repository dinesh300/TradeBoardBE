import sqlite3
import accelpix_service
DB_PATH = "market_data.db"

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
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    default_price = 0  # or use your OPEN_TRACKER if available
    timeframe = "INIT"  # or calculate current timeframe

    # Insert into anomalies_entry with the correct anomaly type
    c.execute('''
        INSERT INTO anomalies_entry (
            stock, anomaly_type, market_open, tpos, action, status, current_price, threshold_price, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
    symbol.upper(), type_.lower(), default_price, timeframe, "Monitoring", "0", default_price, default_price, now))

    conn.commit()
    conn.close()
    print(f"🟢 Inserted anomaly entry and added {symbol.upper()} with type {type_} to anomaly_tickers.")


    accelpix_service.ANOMALY_TICKERS = load_anomaly_tickers()


def remove_anomaly_symbol(symbol: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM anomaly_tickers WHERE ticker = ?", (symbol.upper(),))
    conn.commit()
    conn.close()



# === Anomaly Tickers Utilities ===
def load_anomaly_tickers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ensure anomaly_tickers table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS anomaly_tickers (
            ticker TEXT PRIMARY KEY,
            type TEXT DEFAULT ''
        )
    """)
    conn.commit()

    # Load anomaly tickers
    c.execute("SELECT * FROM anomaly_tickers")
    rows = c.fetchall()

    # Also ensure an initial anomalies_entry exists for each
    for row in rows:
        ticker = row[0].upper()
        anomaly_type = row[1].lower()

        # Check if entry already exists for today
        c.execute('''
            SELECT 1 FROM anomalies_entry
            WHERE stock = ? AND date(time) = date('now')
        ''', (ticker,))
        exists = c.fetchone()

        if not exists:
            from datetime import datetime
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            default_price = 0  # or use your OPEN_TRACKER if available
            timeframe = "INIT"  # or calculate current timeframe
            c.execute('''
                INSERT INTO anomalies_entry (
                    stock, anomaly_type, market_open, tpos, action, status, current_price, threshold_price, time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ticker, anomaly_type, default_price, timeframe, "Monitoring", "0", default_price, default_price, now))
            print(f"🟢 Inserted initial entry for {ticker} during load")

    conn.commit()
    conn.close()

    return {row[0].upper(): row[1].lower() for row in rows}


def migrate_anomaly_tickers_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE anomaly_tickers ADD COLUMN type TEXT DEFAULT ''")
        conn.commit()
    except sqlite3.OperationalError:
        # Ignore if column already exists
        pass
    finally:
        conn.close()



def update_last_trade_price(ticker: str, price: float):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscribed_symbols SET last_trade_price = ? WHERE symbol = ?",
            (price, ticker)
        )
        conn.commit()
    except Exception as e:
        print(f"Failed to update last_trade_price for {ticker}: {e}")
    finally:
        conn.close()


# config.py (additional functions)

def insert_anomaly_entry(ticker,anomaly_type, market_open,tpos,action, threshold_price, price, current_time):
    print("Im inside insert_anomaly_entry Function")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO anomalies_entry (
            stock,anomaly_type, market_open, tpos, action, status, current_price, threshold_price, time
        ) VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
    ''', (ticker,anomaly_type, market_open, tpos, action, "0", price, threshold_price, current_time))
    print("Data inserted anamoly type : ", anomaly_type)
    conn.commit()
    conn.close()

def get_high_price_for_ticker(ticker, start_time, end_time):
    # Assuming you have stored trades in a table, or you're able to retrieve them from a data source
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT MAX(price) FROM trades WHERE ticker = ? AND time BETWEEN ? AND ?
    """, (ticker, start_time, end_time))
    high_price = c.fetchone()[0]
    conn.close()
    return high_price



def update_anomaly_action(ticker, action_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE anomalies_entry
        SET action = ?
        WHERE stock = ? AND action = 'No Breakout'
        ORDER BY time DESC LIMIT 1
    ''', (action_text, ticker))
    conn.commit()
    conn.close()


def update_current_price(ticker, price):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get the latest row ID for this ticker
    c.execute('''
        SELECT rowid FROM anomalies_entry
        WHERE stock = ?
        ORDER BY time DESC
        LIMIT 1
    ''', (ticker,))
    result = c.fetchone()

    if result:
        rowid = result[0]
        c.execute('''
            UPDATE anomalies_entry
            SET current_price = ?
            WHERE rowid = ?
        ''', (price, rowid))
        conn.commit()
    conn.close()


def update_anomaly_open_and_timeframe(ticker, open_price, timeframe):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE anomalies_entry
        SET market_open = ?, tpos = ?
        WHERE stock = ? AND time = (SELECT MAX(time) FROM anomalies_entry WHERE stock = ?)
    ''', (open_price, timeframe, ticker, ticker))
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
