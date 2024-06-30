import yfinance as yf
import mplfinance as mpf

if __name__ == "__main__":
    ticker = input("Enter the stock ticker: ").upper()
    period = input("Enter the period (e.g., '1d', '1mo', '1y'): ").strip()
    
    stock_data = yf.download(ticker, period=period)
    
    mpf.plot(stock_data, type='candle', style='yahoo', title=f'Candlestick Chart for {ticker} ({period})')
