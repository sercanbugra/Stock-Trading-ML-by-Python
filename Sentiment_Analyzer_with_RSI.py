import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import time
import random
from datetime import datetime, timedelta
import concurrent.futures

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Function to parse date strings
def parse_date(date_str):
    if date_str == "Today":
        return datetime.now().date()
    elif date_str == "Yesterday":
        return datetime.now().date() - timedelta(1)
    else:
        return pd.to_datetime(date_str).date()

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

# Parameters
n = 2  # Number of recent news to consider
tickers = get_sp500_tickers()

# List of user agents to rotate
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'
]

# Function to fetch news table and RSI for a single ticker
def fetch_news_and_rsi(ticker):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    encoded_ticker = quote(ticker)
    url = finviz_url + encoded_ticker
    user_agent = random.choice(user_agents)
    req = Request(url=url, headers={'user-agent': user_agent})
    try:
        resp = urlopen(req)
        html = BeautifulSoup(resp, features="lxml")
        news_table = html.find(id='news-table')
        
        # Extracting RSI value using more robust method
        rsi_text = html.find(text='RSI (14)')
        if rsi_text:
            rsi = rsi_text.find_next(class_='snapshot-td2').text
            rsi = float(rsi)
        else:
            rsi = None
        
        return ticker, news_table, rsi
    except HTTPError as e:
        print(f"HTTPError for {ticker}: {e}")
        return ticker, None, None
    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return ticker, None, None
    finally:
        time.sleep(random.uniform(1, 3))  # Add delay

# Function to fetch news tables and RSI concurrently
def fetch_news_and_rsi_tables(tickers):
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ticker = {executor.submit(fetch_news_and_rsi, ticker): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker, news_table, rsi = future.result()
            results[ticker] = (news_table, rsi)
    return results

# Function to parse news headlines and dates
def parse_news(news_tables):
    parsed_news = []
    for ticker, (news_table, rsi) in news_tables.items():
        if news_table is None:
            continue
        for x in news_table.findAll('tr')[:n]:
            text = x.a.get_text()
            date_scrape = x.td.text.split()

            if len(date_scrape) == 1:
                time = date_scrape[0]
                date = "Today"  # Assuming single time means today's news
            else:
                date = date_scrape[0]
                time = date_scrape[1]

            parsed_news.append([ticker, date, time, text, rsi])
    return parsed_news

# Sentiment Analysis
def calculate_sentiment(parsed_news):
    analyzer = SentimentIntensityAnalyzer()
    columns = ['Ticker', 'Date', 'Time', 'Headline', 'RSI']
    news = pd.DataFrame(parsed_news, columns=columns)
    news['Date'] = news['Date'].apply(parse_date)
    scores = news['Headline'].apply(analyzer.polarity_scores).tolist()
    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores)
    return news

# Main Function
def main():
    # Fetch news tables and RSI values
    news_tables = fetch_news_and_rsi_tables(tickers)

    # Parse news headlines and dates
    parsed_news = parse_news(news_tables)

    # Calculate sentiment scores
    news_sentiment = calculate_sentiment(parsed_news)

    # Output to Excel file
    news_sentiment.to_excel("sentiment_scores_sp500.xlsx", index=False)

    # Plotting
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Pick top and bottom 10 stocks based on average sentiment scores
    avg_sentiment = news_sentiment.groupby('Ticker')['compound'].mean().sort_values()
    top_10 = avg_sentiment.tail(10)
    bottom_10 = avg_sentiment.head(10)

    # Extract corresponding RSI values
    top_10_rsi = news_sentiment[news_sentiment['Ticker'].isin(top_10.index)].groupby('Ticker')['RSI'].first()
    bottom_10_rsi = news_sentiment[news_sentiment['Ticker'].isin(bottom_10.index)].groupby('Ticker')['RSI'].first()

    # Plot sentiment scores with RSI values on a secondary axis

    # Plot sentiment scores
    color = 'tab:blue'
    ax1.set_xlabel('Ticker')
    ax1.set_ylabel('Average Sentiment Score', color=color)
    ax1.bar(top_10.index, top_10.values, color='green', label='Top 10 Stocks')
    ax1.bar(bottom_10.index, bottom_10.values, color='red', label='Bottom 10 Stocks')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    # Create a secondary y-axis for RSI values
    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('RSI', color=color)

    # Convert RSI values to numeric (float) type
    top_10_rsi = top_10_rsi.astype(float)
    bottom_10_rsi = bottom_10_rsi.astype(float)

    # Ensure the order of the tickers for plotting is consistent
    ax2.scatter(top_10_rsi.index, top_10_rsi.values, color='blue', marker='o', label='Top 10 Stocks RSI')
    ax2.scatter(bottom_10_rsi.index, bottom_10_rsi.values, color='blue', marker='*', label='Bottom 10 Stocks RSI')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.axhline(70, color='grey', linestyle='--', linewidth=0.7)
    ax2.axhline(30, color='grey', linestyle='--', linewidth=0.7)

    # Adding RSI value labels
    for i, txt in enumerate(top_10_rsi.values):
        ax2.annotate(f'{txt:.2f}', (top_10_rsi.index[i], top_10_rsi.values[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='blue')

    for i, txt in enumerate(bottom_10_rsi.values):
        ax2.annotate(f'{txt:.2f}', (bottom_10_rsi.index[i], bottom_10_rsi.values[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='blue')

    fig.tight_layout()
    plt.title('Average Sentiment Scores and RSI for Top and Bottom 10 S&P 500 Stocks')
    plt.xticks(rotation=45, ha='right')
    fig.legend(loc='lower left', bbox_to_anchor=(1,0.85))
    plt.show()

if __name__ == "__main__":
    main()
