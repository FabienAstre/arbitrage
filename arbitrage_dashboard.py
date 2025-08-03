import streamlit as st
import requests

st.set_page_config(page_title="🔁 Real Arbitrage Dashboard", layout="wide")
st.title("🔁 Real Arbitrage Opportunities: Ethereum vs BSC")
st.markdown("Compare swap output amounts on 1inch API for Ethereum and Binance Smart Chain to find arbitrage.")

# Token addresses for Ethereum and BSC
TOKENS = {
    "WETH": {
        "eth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "bsc": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8"
    },
    "USDT": {
        "eth": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        "bsc": "0x55d398326f99059fF775485246999027B3197955"
    }
}

INPUT_AMOUNT = 1 * 10**18  # 1 token with 18 decimals (adjust as needed)

CHAIN_IDS = {
    "Ethereum": 1,
    "BSC": 56
}

def get_1inch_quote(chain_id, from_token, to_token, amount):
    url = f"https://api.1inch.io/v5.0/{chain_id}/quote"
    params = {
        "fromTokenAddress": from_token,
        "toTokenAddress": to_token,
        "amount": str(amount)
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        to_token_amount = int(data['toTokenAmount'])
        decimals = data['toToken']['decimals']
        return to_token_amount / (10 ** decimals)
    except Exception as e:
        st.error(f"API error on chain {chain_id}: {e}")
        # Show raw response text if available for debugging
        if 'res' in locals():
            st.text(f"Response content:\n{res.text}")
        return None

# Sidebar - token selection and amount
st.sidebar.header("Swap Settings")
token_in = st.sidebar.selectbox("From Token", list(TOKENS.keys()), index=0)
token_out = st.sidebar.selectbox("To Token", list(TOKENS.keys()), index=1)

if token_in == token_out:
    st.warning("Please select two different tokens for arbitrage.")
    st.stop()

input_amount = st.sidebar.number_input("Input Amount", min_value=0.0001, value=1.0, step=0.1)

# Convert input amount to 18-decimals integer (adjust if tokens differ in decimals)
input_amount_wei = int(input_amount * (10 ** 18))

# Fetch quotes for Ethereum and BSC
eth_quote = get_1inch_quote(CHAIN_IDS["Ethereum"], TOKENS[token_in]["eth"], TOKENS[token_out]["eth"], input_amount_wei)
bsc_quote = get_1inch_quote(CHAIN_IDS["BSC"], TOKENS[token_in]["bsc"], TOKENS[token_out]["bsc"], input_amount_wei)

if eth_quote is None or bsc_quote is None:
    st.error("Failed to fetch quotes from 1inch API.")
    st.stop()

st.subheader(f"Swap Quotes for {input_amount} {token_in}")

st.markdown(f"- **Ethereum:** {eth_quote:.6f} {token_out}")
st.markdown(f"- **Binance Smart Chain:** {bsc_quote:.6f} {token_out}")

# Calculate arbitrage opportunity
if eth_quote > bsc_quote:
    profit = eth_quote - bsc_quote
    spread_pct = (profit / bsc_quote) * 100
    st.success(f"💰 Buy on BSC, Sell on Ethereum → Potential Profit: {profit:.6f} {token_out} ({spread_pct:.2f}%)")
elif bsc_quote > eth_quote:
    profit = bsc_quote - eth_quote
    spread_pct = (profit / eth_quote) * 100
    st.success(f"💰 Buy on Ethereum, Sell on BSC → Potential Profit: {profit:.6f} {token_out} ({spread_pct:.2f}%)")
else:
    st.info("No arbitrage opportunity detected for selected token pair and amount.")
