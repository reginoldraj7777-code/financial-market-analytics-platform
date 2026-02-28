import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Financial Market Analytics Platform")

df = pd.read_csv("outputs/processed_data.csv")

st.subheader("Dataset Preview")
st.dataframe(df.head())

st.subheader("Price Trend")

fig, ax = plt.subplots()
ax.plot(df["Date"], df["Close"], label="Close Price")
ax.plot(df["Date"], df["SMA_50"], label="SMA 50")
ax.plot(df["Date"], df["SMA_200"], label="SMA 200")

ax.legend()
plt.xticks(rotation=45)

st.pyplot(fig)

st.subheader("Rolling Volatility")

fig2, ax2 = plt.subplots()
ax2.plot(df["Date"], df["Volatility"])
plt.xticks(rotation=45)

st.pyplot(fig2)
