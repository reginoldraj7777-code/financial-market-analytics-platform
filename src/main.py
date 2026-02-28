import os
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Create outputs folder if not exists
os.makedirs("outputs", exist_ok=True)

# Choose stock
symbols = ["AAPL", "MSFT", "TSLA"]

# Download 1 year of daily data
df = yf.download(symbol, period="1y", interval="1d")

# Compute indicators
df["SMA_50"] = df["Close"].rolling(window=50).mean()
df["SMA_200"] = df["Close"].rolling(window=200).mean()
df["Daily_Return"] = df["Close"].pct_change()
df["Volatility_20"] = df["Daily_Return"].rolling(20).std()

# Save processed data
df.to_csv("outputs/processed_data.csv")

# Plot closing price + moving averages
plt.figure(figsize=(12,6))
plt.plot(df["Close"], label="Close Price")
plt.plot(df["SMA_50"], label="SMA 50")
plt.plot(df["SMA_200"], label="SMA 200")
plt.title(f"{symbol} Price with Moving Averages")
plt.legend()
plt.savefig("outputs/price_moving_avg.png")
plt.close()

# Plot volatility
plt.figure(figsize=(12,6))
plt.plot(df["Volatility_20"], label="20-day Volatility")
plt.title(f"{symbol} 20-Day Rolling Volatility")
plt.legend()
plt.savefig("outputs/volatility.png")
plt.close()

print("✅ Processing complete.")
print("Charts saved in outputs/ folder.")# main project code will be placed here

## Project Outputs

### Moving Average Analysis
![Moving Average](screenshots/price_moving_avg.png)

### Volatility Analysis
![Volatility](screenshots/volatility.png)
