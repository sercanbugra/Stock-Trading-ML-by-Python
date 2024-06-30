import yfinance as yf
import pandas as pd
import talib
import mplfinance as mpf
from datetime import datetime
import os
import streamlit as st
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen

stable_sp500_tickers= []

# Function to fetch S&P 500 stock tickers
def get_sp500_tickers():
    sp500_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = urlopen(sp500_url)
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[0].text.strip()
        tickers.append(ticker)
    return tickers

# Fetch S&P 500 tickers
sp500_tickers = get_sp500_tickers()

# Initialize an empty list to store results
cross_above_signals = []

# Iterate over each ticker
for ticker in sp500_tickers:
    try:
        # Fetch the stock data for the past 3 months with daily intervals
        stock = yf.Ticker(ticker)
        data = stock.history(period="3mo", interval="1d")
        
        if data.empty or len(data) < 3:
            continue

        # Calculate the 12-period EMA
        data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()

        # Calculate the 26-period EMA
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()

        # Calculate MACD (the difference between 12-period EMA and 26-period EMA)
        data['MACD'] = data['EMA12'] - data['EMA26']

        # Calculate the 9-period EMA of MACD (Signal Line)
        data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

        # Check if MACD has crossed above the Signal Line for the last 3 consecutive days
        macd_above_signal = all(data['MACD'].iloc[-(i+1)] > data['Signal_Line'].iloc[-(i+1)] for i in range(4))

        if macd_above_signal:
            cross_above_signals.append(ticker)
    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")

# Create a DataFrame from the results
results_df = pd.DataFrame(cross_above_signals, columns=['Ticker'])

# Fetch S&P 500 tickers
stable_sp500_tickers = results_df['Ticker'].tolist()




# List of candlestick patterns available in TA-Lib with explanations and suggestions
patterns = {
   
    'CDLHAMMER': (talib.CDLHAMMER, "Hammer: Bullish reversal.", "Buy stock")
    
}

# Function to analyze stock data
def analyze_stock(stock, output_dir):
    try:
        data = yf.download(stock, period='5d', interval='1h')  # Change period to '5d'
    except Exception as e:
        print(f"Error downloading data for {stock}: {e}")
        return []

    if data.empty:
        return []

    data.reset_index(inplace=True)
    data['Date'] = data['Datetime'].dt.date
    last_candle_date = data['Date'].iloc[-1]

    results = []

    for pattern_name, (pattern_func, explanation, suggestion) in patterns.items():
        result = pattern_func(data['Open'], data['High'], data['Low'], data['Close'])
        if result.iloc[-1] != 0:
            # Save the plot
            plot_filename = os.path.join(output_dir, f"{stock}_{pattern_name}_{last_candle_date}.png")
            mpf.plot(data.set_index('Datetime'), type='candle', style='charles', title=f"{stock} - {pattern_name}", savefig=plot_filename)

            results.append({
                'Stock name': stock,
                'Last candle date': last_candle_date,
                'Candle pattern detected': pattern_name,
                'Explanation': explanation,
                'Suggestion': suggestion,
                'Plot': plot_filename
            })

    return results

# Function to compile results for all stocks
def analyze_stocks(stocks, output_dir):
    all_results = []
    for stock in stocks:
        stock_results = analyze_stock(stock, output_dir)
        all_results.extend(stock_results)
    return all_results

# Create directories for results
current_date = datetime.now().strftime("%Y-%m-%d")
results_dir = "Results"
date_dir = os.path.join(results_dir, current_date)
os.makedirs(date_dir, exist_ok=True)

# Streamlit setup
st.title("Stock Analysis Dashboard")
st.write("This dashboard updates every minute with the latest stock analysis results.")

placeholder = st.empty()

# Main function to run the analysis and update the dashboard
def update_dashboard():
    results = analyze_stocks(stable_sp500_tickers, date_dir)

    # Convert results to DataFrame for better visualization
    df_results = pd.DataFrame(results)

    # Save results to a CSV file
    csv_filename = os.path.join(date_dir, 'sp500_stock_analysis_results.csv')
    df_results.to_csv(csv_filename, index=False)

    # Display results in Streamlit
    refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with placeholder.container():
        st.write(f"Last updated: {refresh_time}")
        st.dataframe(df_results)
        for index, row in df_results.iterrows():
            st.write(f"### {row['Stock name']} - {row['Candle pattern detected']}")
            st.write(f"**Explanation:** {row['Explanation']}")
            st.write(f"**Suggestion:** {row['Suggestion']}")
            st.image(row['Plot'], use_column_width=True)

# Auto-refreshing loop
while True:
    update_dashboard()
    time.sleep(60)
