import streamlit as st
import requests
import sqlite3
import pandas as pd
import datetime
import time

# API URL
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

# Connect to SQLite
conn = sqlite3.connect("bitcoin.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bitcoin_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        price REAL
    )
""")
conn.commit()

# Function to fetch & store Bitcoin price
def fetch_and_store_bitcoin_price():
    try:
        response = requests.get(API_URL)
        data = response.json()
        price = data.get("bitcoin", {}).get("usd", None)

        if price is not None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO bitcoin_prices (timestamp, price) VALUES (?, ?)", (timestamp, price))
            conn.commit()
            st.success(f"✅ Bitcoin price {price} stored at {timestamp}")
        else:
            st.error("⚠️ API response is incorrect:", data)
    
    except Exception as e:
        st.error(f"❌ Error fetching Bitcoin price: {str(e)}")

# Streamlit UI
st.title("📊 Bitcoin Price Dashboard")

# Fetch latest Bitcoin price manually
if st.button("Fetch Latest Price"):
    fetch_and_store_bitcoin_price()

# Load data from database
df = pd.read_sql("SELECT * FROM bitcoin_prices ORDER BY timestamp DESC LIMIT 10", conn)

# Display chart
st.line_chart(df.set_index("timestamp")["price"])
st.write("### Raw Data Table")
st.dataframe(df)

# Close connection when done
conn.close()
