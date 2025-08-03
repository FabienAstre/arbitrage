import streamlit as st
import requests
import pandas as pd
import altair as alt

# Page config and title
st.set_page_config(page_title="🔁 Crypto Price Dashboard", layout="wide")
st.title("🔁 Crypto Price Dashboard")
st.markdown("Fetches live token prices from CoinGecko for popular tokens.")

# Tokens list with CoinGecko IDs
TOKENS = {
    "Ethereum": "ethereum",
    "Binance Coin": "binancecoin",
    "Tether": "tether",
    "Bitcoin": "bitcoin"
}

def get_price(token_id):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id,
        "vs_currencies": "usd"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        price = response.json()[token_id]["usd"]
        return price
    except Exception as e:
        st.error(f"Error fetching {token_id} price: {e}")
        return None

# Fetch prices and build data list
prices_data = []
for name, token_id in TOKENS.items():
    price = get_price(token_id)
    if price is not None:
        prices_data.append({"Token": name, "Price (USD)": price})

# Create dataframe
df = pd.DataFrame(prices_data)

if df.empty:
    st.error("❌ Could not retrieve any price data.")
else:
    # Show price table
    st.subheader("📊 Live Token Prices")
    st.dataframe(df.style.format({"Price (USD)": "${:,.2f}"}), use_container_width=True)

    # Create bar chart of prices
    chart = alt.Chart(df).mark_bar(color="#1f77b4").encode(
        x=alt.X("Token:N", sort=None),
        y=alt.Y("Price (USD):Q"),
        tooltip=["Token", alt.Tooltip("Price (USD):Q", format="$,.2f")]
    ).properties(title="Token Prices (USD)", width=700)

    st.altair_chart(chart, use_container_width=True)
