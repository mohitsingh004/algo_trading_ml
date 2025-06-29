# modules/indicators.py
import pandas as pd
import numpy as np

def compute_rsi(data, window=14):
    """Compute Relative Strength Index"""
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_moving_averages(data, short_window=20, long_window=50):
    """Compute moving averages"""
    data['20_DMA'] = data['Close'].rolling(short_window).mean()
    data['50_DMA'] = data['Close'].rolling(long_window).mean()
    return data

def compute_macd(data, fast=12, slow=26, signal=9):
    """Compute MACD and Signal Line"""
    data['MACD'] = data['Close'].ewm(span=fast, min_periods=0, adjust=False).mean() - \
                   data['Close'].ewm(span=slow, min_periods=0, adjust=False).mean()
    data['Signal_Line'] = data['MACD'].ewm(span=signal, min_periods=0, adjust=False).mean()
    return data