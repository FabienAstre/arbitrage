# arbitrage_dashboard.py

import streamlit as st
import requests

# === CONFIG ===
PANCAKESWAP_API = "https://api.pancakeswap.info/api/v2/tokens/"
BAKERYSWAP_API = "https://api.bakeryswap.org/api/tokens/"
TOKENS = {
    "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    "USDT": "0x55d398326f99059fF775485246999027B3197955",
    "BUSD": "0xe9e7cea3dedca5984780bafc599bd69add087d56"
}

# === FUNCTIONS ===
def get_token_price_pancake(address):
    try:
        r = requests.get(PANCAKESWAP_API + address)
        data = r.json()
        return float(data["data"]["price"])
    except:
        return None

def get_token_price_bakery(address):
    try:
        r = requests.get(BAKERYSWAP_API + address)
        data = r.json()
        return float(data["data"]["price"])
    except:
        return None

def calc_profit(buy_price, sell_price, amount):
    return (sell_price - buy_price) * amount

# === UI ===
st.title("🔁 BSC Arbitrage Dashboard")
token_name = st.selectbox("Select token to compare", list(TOKENS.keys()))
trade_amount = st.number_input("Amount to trade", min_value=0.1, value=10.0, step=0.1)

token_address = TOKENS[token_name]

price_pancake = get_token_price_pancake(token_address)
price_bakery = get_token_price_bakery(token_address)

if price_pancake and price_bakery:
    st.subheader(f"Live Prices for {token_name}")
    st.metric("📈 PancakeSwap", f"${price_pancake:.4f}")
    st.metric("📉 BakerySwap", f"${price_bakery:.4f}")

    if price_pancake > price_bakery:
        profit = calc_profit(price_bakery, price_pancake, trade_amount)
        st.success(f"🟢 Arbitrage: Buy on BakerySwap, sell on PancakeSwap → Profit: ${profit:.2f}")
    elif price_bakery > price_pancake:
        profit = calc_profit(price_pancake, price_bakery, trade_amount)
        st.success(f"🟢 Arbitrage: Buy on PancakeSwap, sell on BakerySwap → Profit: ${profit:.2f}")
    else:
        st.warning("No arbitrage opportunity detected.")
else:
    st.error("❌ Error fetching prices.")
