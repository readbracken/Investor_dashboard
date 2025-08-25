import streamlit as st
import pandas as pd
import datetime

# Title
st.title("📊 Investor Dashboard")

# Sidebar inputs
st.sidebar.header("Investment Inputs")

cash = st.sidebar.number_input("Cash (£)", min_value=0, value=30000, step=1000)
isa = st.sidebar.number_input("ISA (£)", min_value=0, value=19200, step=1000)
gold = st.sidebar.number_input("Gold (£)", min_value=0, value=2000, step=100)
mortgage = st.sidebar.number_input("Mortgage (£)", min_value=0, value=200000, step=1000)

# Date
today = datetime.date.today()

# Portfolio summary
st.subheader("💼 Portfolio Summary")
data = {
    "Asset": ["Cash", "ISA", "Gold", "Mortgage (debt)"],
    "Value (£)": [cash, isa, gold, -mortgage]
}
df = pd.DataFrame(data)

st.table(df)

net_worth = cash + isa + gold - mortgage
st.metric("Net Worth (£)", f"{net_worth:,.0f}")

# Notes
st.subheader("📝 Notes")
notes = st.text_area("Enter notes here (e.g., strategy, thoughts, updates)")
