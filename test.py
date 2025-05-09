import sqlite3

DB_PATH = "market_data.db"

def add_last_trade_price_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Try adding the column (will fail if it already exists)
        cursor.execute("ALTER TABLE subscribed_symbols ADD COLUMN last_trade_price REAL")
        print("Column added successfully.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Column already exists.")
        else:
            raise
    finally:
        conn.commit()
        conn.close()

#add_last_trade_price_column()


def update_last_trade_price(symbol: str, price: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE subscribed_symbols
            SET last_trade_price = ?
            WHERE symbol = ?
        """, (price, symbol))
        conn.commit()
        print(f"Updated {symbol} with price {price}")
    except Exception as e:
        print(f"Error updating price for {symbol}: {e}")
    finally:
        conn.close()

# Example usage:
# update_last_trade_price("TCS-1", 3546.0)
# update_last_trade_price("SBILIFE-1", 546.0)
# update_last_trade_price("INFY-1", 36.0)
# update_last_trade_price("ONGC-1", 7746.0)
# update_last_trade_price("HDFCLIFE-1", 1546.0)
# update_last_trade_price("ITC-1", 86.0)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

def migrate_anomalies_entry_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE anomalies_entry ADD COLUMN anomaly_type TEXT DEFAULT ''")
        conn.commit()
        print("✅ Added 'anomaly_type' column to anomalies_entry table")
    except sqlite3.OperationalError:
        print("⚠️ Column 'anomaly_type' already exists.")
    finally:
        conn.close()

#migrate_anomalies_entry_table()


# Delete all rows
c.execute("DELETE FROM anomalies_entry")

conn.commit()
conn.close()