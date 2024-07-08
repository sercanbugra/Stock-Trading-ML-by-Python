import pandas as pd
from datetime import datetime
import math
import requests
import numpy as np
from bs4 import BeautifulSoup
import mplfinance as mpf
import yfinance as yf
import matplotlib.pyplot as plt

def fetch_html_table(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 '}     
    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code != 200: 
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return None, response.status_code, response.text
    
    soup = BeautifulSoup(response.content, "html.parser")

    if 'Select All' in response.text:
        for span in soup.find_all("span", {'class': 'Fz(0)'}):
            span.replaceWith('')

    table_tags = soup.find_all('table')
    if len(table_tags) == 0:
        print('No tables found on the page!')
        return None
    
    data_frame = pd.read_html(str(table_tags))[0]    
    return data_frame

def generate_combined_stock_charts(source_url, start_date):
    ticker_list = fetch_html_table(source_url)
    if ticker_list is None or ticker_list.empty:
        raise RuntimeError('Failed to retrieve Yahoo trending tickers')
        
    num_rows = math.ceil(math.sqrt(len(ticker_list)))
    num_cols = math.ceil(math.sqrt(len(ticker_list)))
    if num_rows * num_cols - len(ticker_list) >= num_rows:
        num_rows -= 1
    
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(num_cols * 5, num_rows * 5), dpi=200)
    plt.subplots_adjust(wspace=0.2, hspace=0.5)
    
    stock_data = yf.download(ticker_list.Symbol.to_list(), start=start_date, interval='1d')
    stock_data = stock_data.reset_index()
    stock_data['Date'] = pd.to_datetime(stock_data['Date'], errors='coerce')
    stock_data.set_index('Date', inplace=True)
    
    for idx, symbol in enumerate(ticker_list.Symbol):
        row, col = divmod(idx, num_cols)
        axis = axes[row, col]
        
        symbol_data = stock_data.xs(symbol, level=1, axis=1).dropna()
        if symbol_data.empty:
            continue
        
        title_name = (ticker_list[ticker_list['Symbol'] == symbol].iloc[0])['Name'][:16]
        
        current_price = symbol_data['Close'][-1]
        previous_price = symbol_data['Close'][-2]
        pct_change = ((current_price - previous_price) / previous_price) * 100
        
        title_color = 'darkgreen' if pct_change >= 0 else 'red'
        facecolor = 'palegreen' if pct_change >= 0 else 'mistyrose'
        todaytrendsymbol = '⇧' if pct_change >= 0 else '⇩'
        
        mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
        s = mpf.make_mpf_style(marketcolors=mc, facecolor=facecolor)
        
        mpf.plot(symbol_data, type='candle', ax=axis, style=s)
        axis.set_title(f"{title_name}\n({symbol}) {current_price:.2f}{todaytrendsymbol}{pct_change:.2f}%", color=title_color, fontsize=10)
    
    # Remove any unused axes
    for j in range(idx + 1, num_rows * num_cols):
        fig.delaxes(axes.flatten()[j])
    
    today_date = datetime.now().strftime("%Y-%m-%d")
    fig.suptitle(f'{source_url}\n{start_date} ~ {today_date}', fontweight="bold", fontsize=16)
    fig.tight_layout()
    fig.savefig('stock_screener_combined.jpg', dpi=200, bbox_inches='tight')

    return True

if __name__ == '__main__':
    yahoo_url = 'https://finance.yahoo.com/trending-tickers'
    generate_combined_stock_charts(yahoo_url, start_date='2023-01-01')
