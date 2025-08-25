import streamlit as st
import yfinance as yf
import numpy as np

st.set_page_config(page_title="Moonshot Allocator", layout="wide")

st.title("🚀 Moonshot Allocator Dashboard")
st.markdown("This dashboard allocates **60%** between Tesla, Nvidia, and Oxford Nanopore based on weighted technical & fundamental signals. "
            "The other **40% is fixed in the S&P 500.**")

# --- Stock symbols
symbols = {
    "Tesla": "TSLA",
    "Nvidia": "NVDA",
    "Oxford Nanopore": "ONT.L"  # London ticker for Oxford Nanopore
}

# --- Weights for signals (these can be tuned later)
weights = {
    "RSI": 0.25,
    "MACD": 0.20,
    "P/E": 0.20,
    "Debt/Equity": 0.15,
    "Profit Margin": 0.20
}

# --- Helper functions
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")
    return stock, hist

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(prices):
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return (macd.iloc[-1] - signal.iloc[-1])

def normalize(value, low, high):
    """Normalize indicator into 0-1 score"""
    return max(0, min(1, (value - low) / (high - low)))

def get_fundamentals(stock):
    info = stock.info
    pe = info.get("trailingPE", None)
    debt_equity = info.get("debtToEquity", None)
    profit_margin = info.get("profitMargins", None)
    return pe, debt_equity, profit_margin

# --- Calculate scores
scores = {}
for name, ticker in symbols.items():
    try:
        stock, hist = get_stock_data(ticker)
        close_prices = hist["Close"]

        # Technicals
        rsi = calculate_rsi(close_prices)
        macd = calculate_macd(close_prices)

        rsi_score = 1 - normalize(rsi, 30, 70)  # Overbought = low score, Oversold = high score
        macd_score = normalize(macd, -5, 5)

        # Fundamentals
        pe, debt_equity, profit_margin = get_fundamentals(stock)

        pe_score = 1 - normalize(pe if pe else 50, 10, 40)
        debt_score = 1 - normalize(debt_equity if debt_equity else 100, 0, 200)
        profit_score = normalize(profit_margin if profit_margin else 0.1, 0, 0.3)

        # Weighted total
        total_score = (
            weights["RSI"] * rsi_score +
            weights["MACD"] * macd_score +
            weights["P/E"] * pe_score +
            weights["Debt/Equity"] * debt_score +
            weights["Profit Margin"] * profit_score
        )

        scores[name] = total_score

    except Exception as e:
        scores[name] = 0

# --- Convert scores into allocation
total = sum(scores.values())
allocations = {name: (score / total) * 60 for name, score in scores.items()} if total > 0 else {n: 20 for n in symbols}

# --- Display results
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Raw Scores")
    st.write(scores)

with col2:
    st.subheader("💰 Portfolio Allocation")
    st.write({**allocations, "S&P 500": 40})

st.subheader("📈 Notes")
st.markdown("""
- RSI below 30 = good (oversold), above 70 = bad (overbought)  
- MACD positive = good, negative = bad  
- Lower P/E and Debt/Equity = better  
- Higher profit margin = better  
""")
