import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import yfinance as yf

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

# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Fetch S&P 500 tickers
sp500_tickers = get_sp500_tickers()

# Initialize an empty list to store results
results = []

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

        # Calculate RSI
        data['RSI'] = calculate_rsi(data)

        # Check if MACD has crossed above the Signal Line for the last 3 consecutive days
        macd_above_signal = all(data['MACD'].iloc[-(i+1)] > data['Signal_Line'].iloc[-(i+1)] for i in range(3))

        if macd_above_signal:
            # Get the latest RSI value
            latest_rsi = data['RSI'].iloc[-1]
            # Append the ticker and RSI value to the results list
            results.append({'Ticker': ticker, 'RSI': latest_rsi})
    except Exception as e:
        print(f"Error processing ticker {ticker}: {e}")

# Create a DataFrame from the results
results_df = pd.DataFrame(results)

# Save the DataFrame to an Excel file
results_df.to_excel('cross_above_signals_with_rsi.xlsx', index=False)

print("Results saved to cross_above_signals_with_rsi.xlsx")
