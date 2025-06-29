import pandas as pd
import numpy as np

def calculate_indicators(df):
    """Calculate technical indicators with robust handling"""
    try:
        # 1. RSI Calculation with proper smoothing
        delta = df['close'].diff(1)
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Use Wilder's smoothing (EMA with alpha=1/14)
        avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
        
        # Avoid division by zero
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        df['rsi'] = rsi
        
        # 2. Moving Averages with min_periods
        df['ma20'] = df['close'].rolling(window=20, min_periods=5).mean()
        df['ma50'] = df['close'].rolling(window=50, min_periods=10).mean()
        
        # 3. MACD for additional confirmation
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema12 - ema26
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        # Cap RSI values between 0-100
        df['rsi'] = df['rsi'].clip(0, 100)
        
        return df
    except Exception as e:
        logging.error(f"❌ Indicator calculation failed: {str(e)}")
        return df

def generate_signals(df):
    """Generate trading signals with multiple conditions"""
    try:
        # Ensure indicators exist
        for col in ['rsi', 'ma20', 'ma50', 'macd', 'signal']:
            if col not in df.columns:
                df[col] = 0
    
        # 1. Buy Conditions
        condition1 = (df['rsi'] < 35) & (df['ma20'] > df['ma50'])  # Original condition
        condition2 = (df['rsi'] < 40) & (df['macd'] > df['signal']) & (df['ma20'] > df['ma50'])  # MACD confirmation
        condition3 = (df['close'] < df['ma20'] * 0.98) & (df['rsi'] < 45)  # Dip buying
        
        df['buy_signal'] = condition1 | condition2 | condition3
        
        # 2. Sell Conditions
        sell_condition1 = (df['rsi'] > 65)  # Overbought
        sell_condition2 = (df['ma20'] < df['ma50'])  # Death cross
        sell_condition3 = (df['macd'] < df['signal']) & (df['rsi'] > 60)  # MACD bearish
        
        df['sell_signal'] = sell_condition1 | sell_condition2 | sell_condition3
        
        return df
    except Exception as e:
        logging.error(f"❌ Signal generation failed: {str(e)}")
        df['buy_signal'] = False
        df['sell_signal'] = False
        return df