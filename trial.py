import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_sp500_symbols():
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500 = table[0]
    symbols = sp500['Symbol'].tolist()
    # Some symbols used in S&P 500 table might not be directly compatible with Yahoo Finance API (e.g., BRK.B -> BRK-B)
    symbols = [symbol.replace('.', '-') for symbol in symbols]
    return symbols


def analyze_stocks(stock_symbols):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)  # Ensure we have 20 trading days
    results_list = []

    for symbol in stock_symbols:
        try:
            stock_data = yf.download(symbol, start=start_date, end=end_date, progress=False)

            if stock_data.empty:
                print(f"No data found for {symbol}. Skipping...")
                continue

            min_low = stock_data['Low'].min()
            current_close = stock_data['Close'].iloc[-1]
            difference = ((current_close - min_low) / min_low) * 100  # Calculate difference in percentage

            # Adjusted criterion for demonstration
            if current_close <= min_low * 1.05:  # Now checking within 5% of the 20-day minimum
                results_list.append({
                    'Stock': symbol,
                    'Current Price': current_close,
                    '20-Day Min': min_low,
                    'Difference (%)': difference
                })
        except Exception as e:
            print(f"Failed to download {symbol}: {e}")
            continue

    print(f"Processed {len(stock_symbols)} stocks.")
    print(f"Found {len(results_list)} stocks meeting the criteria.")
    return pd.DataFrame(results_list)


def save_html_dashboard(results_df, output_path):
    if results_df.empty:
        print("No matching stocks found.")
        return

    # Round numerical columns to 2 decimal places
    results_df = results_df.round(2)

    # Start HTML and add a style section for custom styling
    html_output = """
    <html>
    <head>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            text-align: right;
            padding: 8px;
            border: 1px solid #ddd;
            font-size: 12pt;
            font-family: Calibri, sans-serif;
        }
        th {
            background-color: #4C72B0;
            color: white;
        }
        tr:nth-child(even) {background-color: #f2f2f2;}
        .highlight { background-color: lightcoral; }
    </style>
    </head>
    <body>
    <table>
    <tr><th>Stock</th><th>Current Price</th><th>20-Day Min</th><th>Difference (%)</th></tr>
    """

    # Iterate through DataFrame rows to add table data
    for index, row in results_df.iterrows():
        highlight_class = 'highlight' if row['Difference (%)'] < 0 else ''
        html_output += f"<tr class=\"{highlight_class}\"><td>{row['Stock']}</td><td>{row['Current Price']}</td><td>{row['20-Day Min']}</td><td>{row['Difference (%)']}</td></tr>"

    # Close HTML tags
    html_output += """
    </table>
    </body>
    </html>
    """

    # Write HTML string to file
    with open(output_path, 'w') as file:
        file.write(html_output)

    print(f"Dashboard saved to {output_path}")


if __name__ == "__main__":
    sp500_symbols = fetch_sp500_symbols()
    results_df = analyze_stocks(sp500_symbols)

    if not results_df.empty:
        output_path = 'sp500_stock_dashboard.html'
        save_html_dashboard(results_df, output_path)
    else:
        print("No data to display in the dashboard.")