import pandas as pd
import requests
from datetime import datetime, timedelta
import concurrent.futures
import time

# Fetch the list of S&P 500 stocks
sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
sp500_table = pd.read_html(sp500_url)[0]
sp500_symbols = sp500_table['Symbol'].tolist()

# Define headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Function to scrape Finviz for a given stock symbol
def scrape_finviz(symbol):
    url = f"https://finviz.com/quote.ashx?t={symbol}&p=d"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()  # Return an empty DataFrame on failure
    
    tables = pd.read_html(response.text)
    if len(tables) > 8:
        df = tables[8]
        df['Symbol'] = symbol
        return df
    return pd.DataFrame()

# Function to process each stock symbol
def process_symbol(symbol):
    try:
        df = scrape_finviz(symbol)
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df[df['Date'] >= current_date - timedelta(days=7)]
            return df if not df.empty else None
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
    return None

# Current date
current_date = datetime.now()

# Use concurrent futures to speed up the process
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_symbol, symbol): symbol for symbol in sp500_symbols}
    results = []
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            results.append(result)

# Concatenate all dataframes
if results:
    final_df = pd.concat(results, ignore_index=True)
    print("Filtered DataFrame with comments within the last 7 days:")
    print(final_df)

    # Write the final dataframe to an Excel file
    output_file = "sp500_price_target_changes.xlsx"
    with pd.ExcelWriter(output_file) as writer:
        final_df.to_excel(writer, index=False)
    print(f"Data saved to {output_file}")
else:
    print("No data found within the last 7 days.")
