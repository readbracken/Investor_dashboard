import streamlit as st
import pandas as pd
import datetime

# Title
st.title("📊 Investor Dashboard")

# Sidebar inputs
st.sidebar.header("Investment Inputs")
cash = st.sidebar.number_input("Cash (£)", min_value=0, value=30000)
isa = st.sidebar.number_input("ISA (£)", min_value=0, value=19200)
gold = st.sidebar.number_input("Gold (£)", min_value=0, value=2000)
mortgage = st.sidebar.number_input("Mortgage (£)", min_value=0, value=200000)

# Date
today = datetime.date.today()

# Portfolio summary
st.subheader("💼 Portfolio Summary")
data = {
    "Asset": ["Cash", "ISA", "Gold", "Mortgage"],
    "Value (£)": [cash, isa, gold, -mortgage],
}
df = pd.DataFrame(data)
st.table(df)

# Net worth
net_worth = cash + isa + gold - mortgage
st.metric("Net Worth (£)", f"{net_worth:,.0f}")

# Notes
st.caption(f"Updated on {today}")
