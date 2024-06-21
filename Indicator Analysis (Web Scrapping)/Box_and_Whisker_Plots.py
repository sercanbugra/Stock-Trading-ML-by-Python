import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd

def get_stock_data(tickers, period):
    data = {}
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        data[ticker] = hist['Close']
    return data

def plot_combined_box_and_whisker(data, period):
    plt.figure(figsize=(12, 8))
    box_data = [data[ticker].dropna() for ticker in data]  # Drop NA values for plotting
    plt.boxplot(box_data, vert=False, patch_artist=True, boxprops=dict(facecolor='lightblue', color='blue'), medianprops=dict(color='red'))
    plt.yticks(range(1, len(data) + 1), data.keys())
    plt.title(f'Box and Whisker Plots for Multiple Stocks ({period})')
    plt.xlabel('Closing Price')
    plt.ylabel('Stock Ticker')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    tickers = input("Enter the stock tickers separated by commas: ").upper().split(',')
    period = input("Enter the period (e.g., '1mo', '3mo', '6mo', '1y'): ").strip()
    
    tickers = [ticker.strip() for ticker in tickers]
    stock_data = get_stock_data(tickers, period)
    
    if all(stock_data[ticker].empty for ticker in tickers):
        print("No data found for the given tickers and period.")
    else:
        plot_combined_box_and_whisker(stock_data, period)
