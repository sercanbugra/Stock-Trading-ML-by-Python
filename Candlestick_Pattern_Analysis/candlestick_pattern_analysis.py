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

mytickerlist= ["SOUN","NVDA","MU","HOLO","ETN","DELL","GLW","CVX",
               "AVGO","BABA","AMD","SNPS","GME","CEG","LLY"
]




# List of candlestick patterns available in TA-Lib with explanations and suggestions
patterns = {
    'CDL2CROWS': (talib.CDL2CROWS, "Two Crows: Potential bearish reversal pattern.", "Sell stock"),
    'CDL3BLACKCROWS': (talib.CDL3BLACKCROWS, "Three Black Crows: Indicates strong bearish sentiment.", "Sell stock"),
    'CDL3INSIDE': (talib.CDL3INSIDE, "Three Inside Up/Down: Potential trend reversal.", "Watch closely"),
    'CDL3LINESTRIKE': (talib.CDL3LINESTRIKE, "Three-Line Strike: Continuation pattern.", "Hold stock"),
    'CDL3OUTSIDE': (talib.CDL3OUTSIDE, "Three Outside Up/Down: Strong trend reversal.", "Watch closely"),
    'CDL3STARSINSOUTH': (talib.CDL3STARSINSOUTH, "Three Stars In The South: Bullish reversal.", "Buy stock"),
    'CDL3WHITESOLDIERS': (talib.CDL3WHITESOLDIERS, "Three White Soldiers: Indicates strong bullish sentiment.", "Buy stock"),
    'CDLABANDONEDBABY': (talib.CDLABANDONEDBABY, "Abandoned Baby: Strong reversal signal.", "Watch closely"),
    'CDLADVANCEBLOCK': (talib.CDLADVANCEBLOCK, "Advance Block: Potential bearish reversal.", "Sell stock"),
    'CDLBELTHOLD': (talib.CDLBELTHOLD, "Belt-hold: Trend reversal pattern.", "Watch closely"),
    'CDLBREAKAWAY': (talib.CDLBREAKAWAY, "Breakaway: Potential reversal.", "Watch closely"),
    'CDLCLOSINGMARUBOZU': (talib.CDLCLOSINGMARUBOZU, "Closing Marubozu: Continuation pattern.", "Hold stock"),
    'CDLCONCEALBABYSWALL': (talib.CDLCONCEALBABYSWALL, "Concealing Baby Swallow: Bullish reversal.", "Buy stock"),
    'CDLCOUNTERATTACK': (talib.CDLCOUNTERATTACK, "Counterattack: Reversal pattern.", "Watch closely"),
    'CDLDARKCLOUDCOVER': (talib.CDLDARKCLOUDCOVER, "Dark Cloud Cover: Bearish reversal.", "Sell stock"),
    'CDLDOJI': (talib.CDLDOJI, "Doji: Indicates indecision.", "Watch closely"),
    'CDLDOJISTAR': (talib.CDLDOJISTAR, "Doji Star: Potential reversal.", "Watch closely"),
    'CDLDRAGONFLYDOJI': (talib.CDLDRAGONFLYDOJI, "Dragonfly Doji: Bullish reversal.", "Buy stock"),
    'CDLENGULFING': (talib.CDLENGULFING, "Engulfing: Strong reversal pattern.", "Watch closely"),
    'CDLEVENINGDOJISTAR': (talib.CDLEVENINGDOJISTAR, "Evening Doji Star: Bearish reversal.", "Sell stock"),
    'CDLEVENINGSTAR': (talib.CDLEVENINGSTAR, "Evening Star: Bearish reversal.", "Sell stock"),
    'CDLGAPSIDESIDEWHITE': (talib.CDLGAPSIDESIDEWHITE, "Up/Down-gap side-by-side white lines: Continuation pattern.", "Hold stock"),
    'CDLGRAVESTONEDOJI': (talib.CDLGRAVESTONEDOJI, "Gravestone Doji: Bearish reversal.", "Sell stock"),
    'CDLHAMMER': (talib.CDLHAMMER, "Hammer: Bullish reversal.", "Buy stock"),
    'CDLHANGINGMAN': (talib.CDLHANGINGMAN, "Hanging Man: Bearish reversal.", "Sell stock"),
    'CDLHARAMI': (talib.CDLHARAMI, "Harami: Reversal pattern.", "Watch closely"),
    'CDLHARAMICROSS': (talib.CDLHARAMICROSS, "Harami Cross: Stronger reversal pattern.", "Watch closely"),
    'CDLHIGHWAVE': (talib.CDLHIGHWAVE, "High-Wave: Indicates indecision.", "Watch closely"),
    'CDLHIKKAKE': (talib.CDLHIKKAKE, "Hikkake: Continuation pattern.", "Hold stock"),
    'CDLHIKKAKEMOD': (talib.CDLHIKKAKEMOD, "Modified Hikkake: Continuation pattern.", "Hold stock"),
    'CDLHOMINGPIGEON': (talib.CDLHOMINGPIGEON, "Homing Pigeon: Bullish reversal.", "Buy stock"),
    'CDLIDENTICAL3CROWS': (talib.CDLIDENTICAL3CROWS, "Identical Three Crows: Strong bearish reversal.", "Sell stock"),
    'CDLINNECK': (talib.CDLINNECK, "In-Neck: Continuation pattern.", "Hold stock"),
    'CDLINVERTEDHAMMER': (talib.CDLINVERTEDHAMMER, "Inverted Hammer: Bullish reversal.", "Buy stock"),
    'CDLKICKING': (talib.CDLKICKING, "Kicking: Strong trend reversal.", "Watch closely"),
    'CDLKICKINGBYLENGTH': (talib.CDLKICKINGBYLENGTH, "Kicking by length: Reversal pattern.", "Watch closely"),
    'CDLLADDERBOTTOM': (talib.CDLLADDERBOTTOM, "Ladder Bottom: Bullish reversal.", "Buy stock"),
    'CDLLONGLEGGEDDOJI': (talib.CDLLONGLEGGEDDOJI, "Long Legged Doji: Indicates indecision.", "Watch closely"),
    'CDLLONGLINE': (talib.CDLLONGLINE, "Long Line Candle: Indicates strong sentiment.", "Watch closely"),
    'CDLMARUBOZU': (talib.CDLMARUBOZU, "Marubozu: Strong continuation.", "Hold stock"),
    'CDLMATCHINGLOW': (talib.CDLMATCHINGLOW, "Matching Low: Bullish reversal.", "Buy stock"),
    'CDLMATHOLD': (talib.CDLMATHOLD, "Mat Hold: Continuation pattern.", "Hold stock"),
    'CDLMORNINGDOJISTAR': (talib.CDLMORNINGDOJISTAR, "Morning Doji Star: Bullish reversal.", "Buy stock"),
    'CDLMORNINGSTAR': (talib.CDLMORNINGSTAR, "Morning Star: Bullish reversal.", "Buy stock"),
    'CDLONNECK': (talib.CDLONNECK, "On-Neck: Continuation pattern.", "Hold stock"),
    'CDLPIERCING': (talib.CDLPIERCING, "Piercing: Bullish reversal.", "Buy stock"),
    'CDLRICKSHAWMAN': (talib.CDLRICKSHAWMAN, "Rickshaw Man: Indicates indecision.", "Watch closely"),
    'CDLRISEFALL3METHODS': (talib.CDLRISEFALL3METHODS, "Rising/Falling Three Methods: Continuation pattern.", "Hold stock"),
    'CDLSEPARATINGLINES': (talib.CDLSEPARATINGLINES, "Separating Lines: Continuation pattern.", "Hold stock"),
    'CDLSHOOTINGSTAR': (talib.CDLSHOOTINGSTAR, "Shooting Star: Bearish reversal.", "Sell stock"),
    'CDLSHORTLINE': (talib.CDLSHORTLINE, "Short Line Candle: Indicates weak sentiment.", "Watch closely"),
    'CDLSPINNINGTOP': (talib.CDLSPINNINGTOP, "Spinning Top: Indicates indecision.", "Watch closely"),
    'CDLSTALLEDPATTERN': (talib.CDLSTALLEDPATTERN, "Stalled Pattern: Reversal pattern.", "Watch closely"),
    'CDLSTICKSANDWICH': (talib.CDLSTICKSANDWICH, "Stick Sandwich: Bullish reversal.", "Buy stock"),
    'CDLTAKURI': (talib.CDLTAKURI, "Takuri (Dragonfly Doji with very long lower shadow): Bullish reversal.", "Buy stock"),
    'CDLTASUKIGAP': (talib.CDLTASUKIGAP, "Tasuki Gap: Continuation pattern.", "Hold stock"),
    'CDLTHRUSTING': (talib.CDLTHRUSTING, "Thrusting Pattern: Continuation.", "Hold stock"),
    'CDLTRISTAR': (talib.CDLTRISTAR, "Tristar Pattern: Reversal.", "Watch closely"),
    'CDLUNIQUE3RIVER': (talib.CDLUNIQUE3RIVER, "Unique Three River Bottom: Bullish reversal.", "Buy stock"),
    'CDLUPSIDEGAP2CROWS': (talib.CDLUPSIDEGAP2CROWS, "Upside Gap Two Crows: Bearish reversal.", "Sell stock"),
    'CDLXSIDEGAP3METHODS': (talib.CDLXSIDEGAP3METHODS, "Upside/Downside Gap Three Methods: Continuation pattern.", "Hold stock")
}

# Function to analyze stock data
def analyze_stock(stock, output_dir):
    try:
        data = yf.download(stock, period='1mo', interval='4h')  
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
    results = analyze_stocks(mytickerlist, date_dir)

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
