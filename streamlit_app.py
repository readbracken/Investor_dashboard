import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# ---------------------
# CONFIG
# ---------------------
st.set_page_config(page_title="Investor Dashboard", layout="wide")

# Stock tickers
STOCKS = {
    "Tesla": "TSLA",
    "Nvidia": "NVDA",
    "Oxford Nanopore": "ONT.L"  # London Stock Exchange ticker
}

# ---------------------
# FUNCTIONS
# ---------------------

def get_stock_data(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def get_fundamentals(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info 

    fundamentals = {
        "P/E Ratio": info.get("trailingPE", None),
        "Debt to Equity": info.get("debtToEquity", None),
        "Profit Margin": info.get("profitMargins", None)
    }
    return fundamentals

def get_technicals(hist):
    hist["50MA"] = hist["Close"].rolling(window=50).mean()
    hist["200MA"] = hist["Close"].rolling(window=200).mean()

    # RSI Calculation
    delta = hist["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    hist["RSI"] = 100 - (100 / (1 + rs))

    latest = hist.iloc[-1]
    technicals = {
        "50MA > 200MA": 1 if latest["50MA"] > latest["200MA"] else 0,
        "RSI": latest["RSI"]
    }
    return technicals, hist

def score_stock(fundamentals, technicals):
    score = 0
    weights = {
        "P/E Ratio": 0.25,
        "Debt to Equity": 0.20,
        "Profit Margin": 0.25,
        "Golden Cross": 0.15,
        "RSI": 0.15
    }

    # Fundamentals
    if fundamentals["P/E Ratio"] and fundamentals["P/E Ratio"] < 30:
        score += weights["P/E Ratio"]
    if fundamentals["Debt to Equity"] and fundamentals["Debt to Equity"] < 100:
        score += weights["Debt to Equity"]
    if fundamentals["Profit Margin"] and fundamentals["Profit Margin"] > 0.1:
        score += weights["Profit Margin"]

    # Technicals
    if technicals["50MA > 200MA"]:
        score += weights["Golden Cross"]
    if 40 < technicals["RSI"] < 70:  # Healthy RSI
        score += weights["RSI"]

    return score

# ---------------------
# STREAMLIT DASHBOARD
# ---------------------

st.title("📊 Investor Dashboard")

# Portfolio Summary
st.header("💼 Portfolio Summary")
portfolio = pd.DataFrame({
    "Asset": ["Cash", "ISA", "Gold", "Mortgage"],
    "Value (£)": [30000, 19200, 2000, -200000]
})
st.table(portfolio)
st.write("Net Worth (£):", portfolio["Value (£)"].sum())

# Stock Analysis
st.header("📈 Stock Analysis & Allocation")

results = []
for name, ticker in STOCKS.items():
    st.subheader(name)

    try:
        # Get Data
        hist = get_stock_data(ticker)
        fundamentals = get_fundamentals(ticker)
        technicals, hist = get_technicals(hist)

        # Score
        score = score_stock(fundamentals, technicals)
        results.append({"Stock": name, "Score": score})

        # Show Fundamentals
        st.write("**Fundamentals**")
        st.json(fundamentals)

        # Show Technicals
        st.write("**Technicals**")
        st.json(technicals)

        # Show Price Chart
        st.line_chart(hist[["Close", "50MA", "200MA"]])

    except Exception as e:
        st.error(f"Error fetching data for {name}: {e}")

# Allocation
st.subheader("📊 Suggested Allocation (60% Stock Portion)")
if results:
    df_scores = pd.DataFrame(results)
    total_score = df_scores["Score"].sum()
    if total_score > 0:
        df_scores["Allocation %"] = (df_scores["Score"] / total_score) * 60
    else:
        df_scores["Allocation %"] = 0
    st.table(df_scores)
