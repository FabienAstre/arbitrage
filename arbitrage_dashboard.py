import streamlit as st
import requests
import pandas as pd
import altair as alt

# ------------------ Setup ------------------
st.set_page_config(page_title="🔁 Crypto Arbitrage Dashboard", layout="wide")
st.title("🔁 ETH & BSC Arbitrage Opportunities")
st.markdown("Compare token prices between Ethereum and BSC networks to identify potential arbitrage trades.")

# ------------------ Token Setup ------------------
TOKENS = {
    "ETH": {"eth": "ethereum", "bsc": "ethereum"},
    "USDT": {"eth": "tether", "bsc": "tether"},
    "BTC": {"eth": "bitcoin", "bsc": "bitcoin"},
    "BNB": {"eth": "binancecoin", "bsc": "binancecoin"},
}

# ------------------ Price Fetch Function ------------------
def get_price(token_id, vs_currency="usd"):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": token_id, "vs_currencies": vs_currency}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[token_id][vs_currency]
    except:
        return None

# ------------------ Arbitrage Logic ------------------
def check_arbitrage():
    data = []
    for symbol, ids in TOKENS.items():
        eth_price = get_price(ids["eth"])
        bsc_price = get_price(ids["bsc"])

        if eth_price is not None and bsc_price is not None and eth_price != bsc_price:
            spread = round(((eth_price - bsc_price) / bsc_price) * 100, 2)
            better_on = "ETH" if eth_price < bsc_price else "BSC"
            data.append({
                "Token": symbol,
                "ETH Price ($)": eth_price,
                "BSC Price ($)": bsc_price,
                "Spread (%)": spread,
                "Cheaper On": better_on
            })
    return pd.DataFrame(data)

# ------------------ Main App ------------------
st.subheader("📈 Live Price Comparison")

with st.spinner("Loading prices..."):
    df = check_arbitrage()

if df.empty:
    st.error("❌ Could not retrieve price data or no differences found.")
else:
    # Spread Chart
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Token:N', title="Token"),
        y=alt.Y('Spread (%):Q', title="Spread (%)"),
        color=alt.Color('Cheaper On:N', scale=alt.Scale(domain=["ETH", "BSC"], range=["#5ac8fa", "#34c759"]))
    ).properties(title="📊 Arbitrage Spread by Token")

    st.altair_chart(chart, use_container_width=True)

    # Styled Data Table
    st.subheader("📊 Detailed Arbitrage Table")
    st.dataframe(
        df.style.applymap(
            lambda val: "background-color: #d4edda" if val == "ETH" else (
                "background-color: #f8d7da" if val == "BSC" else ""
            ),
            subset=["Cheaper On"]
        ),
        use_container_width=True
    )

st.caption("Data via CoinGecko | Updated live | Educational use only.")
