import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
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

sp500_tickers = get_sp500_tickers()

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'
]
# Initialize an empty list to store results
cross_above_signals = []

# Iterate over each ticker
for ticker in sp500_tickers:
    # Fetch the stock data for the past 1 month with daily intervals
    stock = yf.Ticker(ticker)
    data = stock.history(period="3mo", interval="1d")
    
    if data.empty:
        continue

    # Calculate the 12-period EMA
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()

    # Calculate the 26-period EMA
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()

    # Calculate MACD (the difference between 12-period EMA and 26-period EMA)
    data['MACD'] = data['EMA12'] - data['EMA26']

    # Calculate the 9-period EMA of MACD (Signal Line)
    data['Signal_Line'] = data['MACD'].ewm(span=9, adjust=False).mean()

     # Check for MACD crossovers in the last 5 days
    for i in range(1, 4):
        if i >= len(data):
            break
        last_row = data.iloc[-i]
        second_last_row = data.iloc[-(i+1)]

        if second_last_row['MACD'] < second_last_row['Signal_Line'] and last_row['MACD'] > last_row['Signal_Line']:
            cross_above_signals.append(ticker)
            break  # No need to check further if one crossover is found in the last 5 days

# Create a DataFrame from the results
results_df = pd.DataFrame(cross_above_signals, columns=['Ticker'])

# Save the DataFrame to an Excel file
results_df.to_excel('cross_above_signals.xlsx', index=False)
#data.to_excel('check.xlsx', index=False)

print("Results saved to cross_above_signals.xlsx")