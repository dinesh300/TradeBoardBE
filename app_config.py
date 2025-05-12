import sqlite3
import os

# ✅ Absolute or relative path to your SQLite DB
DB_PATH = os.path.join(os.path.dirname(__file__), "market_data.db")

def insert_anomaly_entry(ticker, anomaly_type, market_open, tpos, action, threshold_price, price, current_time):
    print("✅ Inside insert_anomaly_entry")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        # 🔄 Fetch latest market_open if already present for ticker
        c.execute('''
            SELECT market_open FROM anomalies_entry
            WHERE stock = ?
            ORDER BY time DESC LIMIT 1
        ''', (ticker,))
        row = c.fetchone()
        previous_market_open = row[0] if row else market_open

        # 📝 Insert anomaly entry
        c.execute('''
            INSERT INTO anomalies_entry (
                stock, anomaly_type, market_open, tpos, action, status,
                current_price, threshold_price, time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ticker,
            anomaly_type,
            previous_market_open,
            tpos,
            action,
            "0",  # default status
            price,
            threshold_price,
            current_time
        ))

        print(f"📥 Inserted anomaly for {ticker} - Type: {anomaly_type}")
        conn.commit()

    except Exception as e:
        print(f"❌ Error inserting anomaly: {e}")

    finally:
        conn.close()
