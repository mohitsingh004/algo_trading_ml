import pandas as pd
import yfinance as yf
import logging
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def fetch_data(symbol, period="5y", interval="1d"):
    """Fetch historical stock data with error handling"""
    logging.info(f"📡 Fetching data for {symbol} | Period: {period} | Interval: {interval}")
    
    try:
        # Fetch data with explicit parameters
        df = yf.download(
            symbol, 
            period=period, 
            interval=interval,
            auto_adjust=True,
            progress=False
        )
        
        if df.empty:
            logging.warning(f"⚠️ Empty data returned for {symbol}")
            return pd.DataFrame()
        
        # Select and rename columns
        if 'Close' not in df.columns:
            logging.error(f"Missing 'Close' column in data for {symbol}")
            return pd.DataFrame()
            
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df.index = pd.to_datetime(df.index)
        
        # Filter out zeros and fill gaps
        df = df[df['volume'] > 0]
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        logging.info(f"📊 Retrieved {len(df)} records for {symbol}")
        return df
    except Exception as e:
        logging.error(f"❌ Failed to fetch data for {symbol}: {str(e)}")
        return pd.DataFrame()