import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="🔁 Crypto Arbitrage Dashboard", layout="wide")

st.title("🔁 ETH & BSC Arbitrage Dashboard")
st.markdown("This dashboard compares prices of popular tokens across Ethereum and Binance Smart Chain (BSC) to identify arbitrage opportunities.")

# List of tokens to compare
TOKENS = {
    "ETH": {"eth": "ethereum", "bsc": "binancecoin"},
    "USDT": {"eth": "tether", "bsc": "tether"},
    "BTC": {"eth": "bitcoin", "bsc": "bitcoin"},
    "BNB": {"eth": "binancecoin", "bsc": "binancecoin"},
}

def get_price(token_id, vs_currency="usd"):
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": token_id,
        "vs_currencies": vs_currency
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        return res.json().get(token_id, {}).get(vs_currency, None)
    except:
        return None

def check_arbitrage():
    rows = []
    for symbol, chains in TOKENS.items():
        eth_price = get_price(chains["eth"])
        bsc_price = get_price(chains["bsc"])

        if eth_price and bsc_price and eth_price != bsc_price:
            spread = round(((eth_price - bsc_price) / bsc_price) * 100, 2)
            better_on = "ETH" if eth_price < bsc_price else "BSC"
            rows.append({
                "Token": symbol,
                "ETH Price (USD)": eth_price,
                "BSC Price (USD)": bsc_price,
                "Spread (%)": spread,
                "Cheaper On": better_on
            })
    return pd.DataFrame(rows)

with st.spinner("Fetching prices..."):
    df = check_arbitrage()

if df.empty:
    st.error("❌ No arbitrage opportunities found or failed to fetch prices.")
else:
    st.success("✅ Arbitrage data loaded!")
    st.dataframe(df.style.applymap(
        lambda val: "background-color: #c6f6d5" if isinstance(val, str) and val in ["ETH", "BSC"] else ""
    ), height=400)

st.caption("Powered by CoinGecko API | Designed for educational use.")
