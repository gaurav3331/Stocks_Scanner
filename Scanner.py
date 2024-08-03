import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import sys
import os

class SuppressStdErr:
    def __enter__(self):
        self._stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        return self

    def __exit__(self, *args):
        sys.stderr.close()
        sys.stderr = self._stderr

def get_all_time_high(stock_ticker):
    try:
        with SuppressStdErr():
            stock = yf.Ticker(stock_ticker)
            hist = stock.history(period="max")

        if hist.empty:
            st.write(f"No data for {stock_ticker}")
            return None, None

        all_time_high = hist['Close'].max()
        latest_close = hist['Close'].iloc[-1]
        
        return all_time_high, latest_close
    except Exception as e:
        st.write(f"Error with {stock_ticker}: {e}")
        return None, None

def scan_stocks(stock_list):
    stocks_breaking_high = []
    
    for stock in stock_list:
        st.write(f"Processing {stock}...")
        all_time_high, latest_close = get_all_time_high(stock)
        if all_time_high is not None and latest_close is not None and latest_close >= all_time_high:
            stocks_breaking_high.append(stock)
    
    return stocks_breaking_high

def load_stock_tickers(filename):
    df = pd.read_csv(filename)
    column_name = 'stock'  # Ensure this matches the column name in your CSV
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in the CSV file.")
    return df[column_name].tolist()

def plot_monthly_chart(stock_ticker):
    stock = yf.Ticker(stock_ticker)
    hist = stock.history(period="1y", interval="1mo")

    fig = go.Figure(data=[go.Candlestick(x=hist.index,
                                         open=hist['Open'],
                                         high=hist['High'],
                                         low=hist['Low'],
                                         close=hist['Close'])])
    fig.update_layout(title=f'Monthly Candlestick Chart for {stock_ticker}',
                      xaxis_title='Date',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)


st.title("Stocks breaking All Time High")

uploaded_file = st.file_uploader("Choose a CSV file with stock tickers", type="csv")

if uploaded_file is not None:
    stock_list = load_stock_tickers(uploaded_file)
    st.write("Scanning stocks, please wait...")
    stocks_breaking_high = scan_stocks(stock_list)
    if stocks_breaking_high:
        st.write("Stocks currently breaking their all-time high:")
        for stock in stocks_breaking_high:
            if st.button(stock):
                plot_monthly_chart(stock)
    else:
        st.write("No stocks are breaking their all-time high at the moment.")
else:
    st.write("Please upload a CSV file to proceed.")

