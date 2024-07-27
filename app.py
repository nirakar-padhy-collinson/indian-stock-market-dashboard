import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Set the page config to use the dark theme
st.set_page_config(
    page_title="Nifty 50 Stock Insights Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="rocket",
)

st.title("Nifty 50 Stock Insights Dashboard")
st.write(
    """The Indian (NSE - Nifty 50 companies) Stock Market Watch Dashboard is a comprehensive tool designed to provide real-time and historical data for stock market analysis. It aggregates key financial metrics, technical indicators, and charting tools to help users make informed investment decisions. This dashboard is tailored to offer both broad overviews and detailed insights into stock performance, facilitating both short-term trading and long-term investment strategies."""
)
st.sidebar.subheader("Project Info")
st.sidebar.write(
    """
This Streamlit app is designed for stock market analysis of nifty50. It provides:
- **Stock Price Charts**
- **Technical Indicators**
- **Fundamental Analysis**

Use the main interface to interact with the data and explore various metrics.
"""
)


# List of Nifty 50 stock tickers
nifty50_stocks = {
    "HDFCBANK.NS": "HDFC Bank Ltd",
    "RELIANCE.NS": "Reliance Industries Ltd",
    "TCS.NS": "Tata Consultancy Services Ltd",
    "INFY.NS": "Infosys Ltd",
    "HINDUNILVR.NS": "Hindustan Unilever Ltd",
    "ICICIBANK.NS": "ICICI Bank Ltd",
    "HDFC.NS": "Housing Development Finance Corporation Ltd",
    "KOTAKBANK.NS": "Kotak Mahindra Bank Ltd",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel Ltd",
    "ITC.NS": "ITC Ltd",
    "ASIANPAINT.NS": "Asian Paints Ltd",
    "BAJFINANCE.NS": "Bajaj Finance Ltd",
    "HCLTECH.NS": "HCL Technologies Ltd",
    "LT.NS": "Larsen & Toubro Ltd",
    "AXISBANK.NS": "Axis Bank Ltd",
    "MARUTI.NS": "Maruti Suzuki India Ltd",
    "SUNPHARMA.NS": "Sun Pharmaceutical Industries Ltd",
    "TITAN.NS": "Titan Company Ltd",
    "ULTRACEMCO.NS": "UltraTech Cement Ltd",
    "WIPRO.NS": "Wipro Ltd",
    "TECHM.NS": "Tech Mahindra Ltd",
    "HDFCLIFE.NS": "HDFC Life Insurance Company Ltd",
    "DIVISLAB.NS": "Divi's Laboratories Ltd",
    "NESTLEIND.NS": "Nestle India Ltd",
    "ADANIPORTS.NS": "Adani Ports and Special Economic Zone Ltd",
    "JSWSTEEL.NS": "JSW Steel Ltd",
    "TATASTEEL.NS": "Tata Steel Ltd",
    "SBILIFE.NS": "SBI Life Insurance Company Ltd",
    "POWERGRID.NS": "Power Grid Corporation of India Ltd",
    "GRASIM.NS": "Grasim Industries Ltd",
    "NTPC.NS": "NTPC Ltd",
    "BPCL.NS": "Bharat Petroleum Corporation Ltd",
    "ONGC.NS": "Oil & Natural Gas Corporation Ltd",
    "HEROMOTOCO.NS": "Hero MotoCorp Ltd",
    "UPL.NS": "UPL Ltd",
    "COALINDIA.NS": "Coal India Ltd",
    "SHREECEM.NS": "Shree Cement Ltd",
    "BAJAJFINSV.NS": "Bajaj Finserv Ltd",
    "BRITANNIA.NS": "Britannia Industries Ltd",
    "EICHERMOT.NS": "Eicher Motors Ltd",
    "BAJAJ-AUTO.NS": "Bajaj Auto Ltd",
    "INDUSINDBK.NS": "IndusInd Bank Ltd",
    "M&M.NS": "Mahindra & Mahindra Ltd",
    "CIPLA.NS": "Cipla Ltd",
    "DRREDDY.NS": "Dr. Reddy's Laboratories Ltd",
    "ADANIENT.NS": "Adani Enterprises Ltd",
    "HINDALCO.NS": "Hindalco Industries Ltd",
    "TATAMOTORS.NS": "Tata Motors Ltd",
}

# Sidebar for user input
selected_ticker: str = str(
    st.sidebar.selectbox("Select Stock Ticker", list(nifty50_stocks.keys()))
)
stock = yf.Ticker(selected_ticker)

st.header(f"Company: {nifty50_stocks[selected_ticker]}")

# Get historical market data
st.subheader("Historical Market Data")
values = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
default_ix = values.index("1y")
period = st.sidebar.selectbox("Select Time Period", values, index=default_ix)

hist = stock.history(period=period)  # .reset_index(drop=True, inplace=True)
# st.line_chart(hist["Close"])

# Select dates from historical prices df
dates = [str(x)[:10] for x in hist.index.to_list()]

# Create a Plotly line chart
fig = go.Figure()

fig.add_trace(go.Scatter(x=dates, y=hist["Close"], mode="lines", name="Close Price"))

fig.update_layout(
    title="Historical Close Prices",
    xaxis_title="Date",
    yaxis_title="Close Price",
    xaxis_rangeslider_visible=False,  # Optional: hide the range slider
)

# Display the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# st.write(hist)
# st.write(stock.info)

# Create subplots and specify the grid size
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    subplot_titles=("OHLC", "Volume"),
    row_width=[0.2, 0.7],
)

# Plot OHLC on the 1st row
fig.add_trace(
    go.Candlestick(
        x=dates,
        open=hist["Open"],
        high=hist["High"],
        low=hist["Low"],
        close=hist["Close"],
    ),
    row=1,
    col=1,
)

# Bar trace for volumes on the 2nd row without legend
fig.add_trace(go.Bar(x=dates, y=hist["Volume"], showlegend=False), row=2, col=1)

# Do not show OHLC's range slider plot
fig.update(layout_xaxis_rangeslider_visible=False)
fig.update_layout(height=1000)

# Streamlit app
st.subheader("OHLC and Volume Plot")
st.plotly_chart(fig, use_container_width=True)


def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(df, period=14):
    df["H-L"] = df["High"] - df["Low"]
    df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)

    df["ATR"] = df["TR"].rolling(window=period).mean()
    return df["ATR"]


hist["RSI"] = calculate_rsi(hist)
hist["ATR"] = calculate_atr(hist)

# Calculate MACD
hist["EMA_12"] = hist["Close"].ewm(span=12, adjust=False).mean()
hist["EMA_26"] = hist["Close"].ewm(span=26, adjust=False).mean()
hist["MACD"] = hist["EMA_12"] - hist["EMA_26"]
hist["Signal_Line"] = hist["MACD"].ewm(span=9, adjust=False).mean()

# Calculate Bollinger Bands
# Moving Avg
hist["SMA_5"] = hist["Close"].rolling(window=5).mean()
hist["SMA_10"] = hist["Close"].rolling(window=10).mean()
hist["SMA_20"] = hist["Close"].rolling(window=20).mean()
hist["SMA_30"] = hist["Close"].rolling(window=30).mean()
hist["STD_20"] = hist["Close"].rolling(window=20).std()
hist["Bollinger_Upper"] = hist["SMA_20"] + (hist["STD_20"] * 2)
hist["Bollinger_Lower"] = hist["SMA_20"] - (hist["STD_20"] * 2)

# Plot Close price and SMA/EMA
st.subheader("Close Price with SMA")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close"))
# fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_5"], mode="lines", name="SMA 5"))
fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_10"], mode="lines", name="SMA 10"))
# fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_20"], mode="lines", name="SMA 20"))
fig.add_trace(go.Scatter(x=hist.index, y=hist["SMA_30"], mode="lines", name="SMA 30"))

fig.update_layout(title="Close Price with SMA", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig)

# Plot RSI
st.subheader("Relative Strength Index (RSI)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], mode="lines", name="RSI"))
fig.add_hline(y=30, line_width=3, line_dash="dash", line_color="green")
fig.add_hline(y=70, line_width=3, line_dash="dash", line_color="red")
fig.update_layout(title="RSI", xaxis_title="Date", yaxis_title="RSI")
st.plotly_chart(fig)

# Plot MACD
st.subheader("MACD and Signal Line")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["MACD"], mode="lines", name="MACD"))
fig.add_trace(
    go.Scatter(x=hist.index, y=hist["Signal_Line"], mode="lines", name="Signal Line")
)
fig.add_hline(y=0, line_width=3, line_dash="dash", line_color="red")
fig.update_layout(title="MACD and Signal Line", xaxis_title="Date", yaxis_title="MACD")
st.plotly_chart(fig)

# Plot Bollinger Bands
st.subheader("Bollinger Bands")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close"))
fig.add_trace(
    go.Scatter(
        x=hist.index, y=hist["Bollinger_Upper"], mode="lines", name="Bollinger Upper"
    )
)
fig.add_trace(
    go.Scatter(
        x=hist.index, y=hist["Bollinger_Lower"], mode="lines", name="Bollinger Lower"
    )
)
fig.update_layout(title="Bollinger Bands", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig)

# Plot ATR
st.subheader("Average True Range (ATR)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist["ATR"], mode="lines", name="ATR"))
fig.update_layout(
    title="Average True Range (ATR)", xaxis_title="Date", yaxis_title="ATR"
)
st.plotly_chart(fig)


# Show share count
st.subheader("Outstanding Company Shares Count")
shares = stock.get_shares_full(start="2022-01-01", end=None)
st.line_chart(shares)

# Show financials
st.subheader("Financials")
st.write("Income Statement:")
st.write(stock.income_stmt, use_container_width=True)
st.write("Quarterly Income Statement:")
st.write(stock.quarterly_income_stmt, use_container_width=True)
st.write("Balance Sheet:")
st.write(stock.balance_sheet, use_container_width=True)
st.write("Quarterly Balance Sheet:")
st.write(stock.quarterly_balance_sheet, use_container_width=True)
st.write("Cash Flow Statement:")
st.dataframe(stock.cashflow, use_container_width=True)
st.write("Quarterly Cash Flow Statement:")
st.write(stock.quarterly_cashflow, use_container_width=True)

# Company Information Table
company_info = stock.info
company_info_df = pd.DataFrame([company_info], index=["HDFC Bank"]).T

# Officers Information Table
officers_df = pd.DataFrame(company_info["companyOfficers"])

# Financial Metrics Table
st.subheader("Financial Metrics")
financial_metrics = {
    "Current Price": company_info["currentPrice"],
    "Previous Close": company_info["previousClose"],
    "Day Low": company_info["dayLow"],
    "Day High": company_info["dayHigh"],
    "Dividend Rate": company_info["dividendRate"],
    "Dividend Yield": company_info["dividendYield"],
    "Market Cap": company_info["marketCap"],
    "Beta": company_info["beta"],
    "Trailing PE": company_info["trailingPE"],
    "Forward PE": company_info["forwardPE"],
    "Revenue Per Share": company_info["revenuePerShare"],
    "Book Value": company_info["bookValue"],
    "Price to Book": company_info["priceToBook"],
    "Earnings Quarterly Growth": company_info["earningsQuarterlyGrowth"],
    "Return on Assets": company_info["returnOnAssets"],
    "Return on Equity": company_info["returnOnEquity"],
    "Revenue Growth": company_info["revenueGrowth"],
    "Operating Margins": company_info["operatingMargins"],
}
financial_metrics_df = pd.DataFrame(
    financial_metrics.items(), columns=["Metric", "Value"]
)
st.dataframe(financial_metrics_df, width=700)

st.subheader("Company Information")
st.dataframe(company_info_df, width=1000)

st.subheader("Company Officers")
st.dataframe(officers_df, use_container_width=True)

# # Show metadata about history and stock info
# st.subheader("Stock Info and History Metadata")
# st.write(stock.info)
# st.write(stock.history_metadata)
