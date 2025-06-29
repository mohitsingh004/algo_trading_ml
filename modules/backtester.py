import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Backtester:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        
    def run_backtest(self, df):
        position = 0
        capital = self.initial_capital
        trades = []
        entry_price = 0
        stop_loss_price = 0
        
        for i in range(len(df)):
            row = df.iloc[i]
            date = df.index[i]
            
            # Stop loss check (5%)
            if position > 0 and row['close'] < stop_loss_price:
                exit_price = row['close']
                pnl = position * (exit_price - entry_price)
                capital += position * exit_price
                
                trades[-1].update({
                    'exit_date': date,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'stop_loss': True
                })
                position = 0
                
            # Buy signal execution
            if row['buy_signal'] and position == 0 and capital > row['close']:
                entry_price = row['close']
                stop_loss_price = entry_price * 0.95
                position_size = min(10, capital // entry_price)  # Position sizing
                position = position_size
                capital -= position * entry_price
                
                trades.append({
                    'entry_date': date,
                    'entry_price': entry_price,
                    'position': position,
                    'stop_loss': stop_loss_price
                })
            
            # Sell signal execution
            elif row['sell_signal'] and position > 0:
                exit_price = row['close']
                pnl = position * (exit_price - entry_price)
                capital += position * exit_price
                
                trades[-1].update({
                    'exit_date': date,
                    'exit_price': exit_price,
                    'pnl': pnl
                })
                position = 0
        
        # Handle open positions at end
        if position > 0 and trades:
            last_row = df.iloc[-1]
            exit_price = last_row['close']
            pnl = position * (exit_price - entry_price)
            capital += position * exit_price
            
            trades[-1].update({
                'exit_date': df.index[-1],
                'exit_price': exit_price,
                'pnl': pnl,
                'open_at_end': True
            })
        
        return pd.DataFrame(trades) if trades else pd.DataFrame()

def backtest_strategy(df, symbol, initial_capital):
    """Wrapper function for backtesting"""
    try:
        bt = Backtester(initial_capital)
        trade_log = bt.run_backtest(df)
        
        if not trade_log.empty:
            # Add symbol column and calculate metrics
            trade_log['symbol'] = symbol
            trade_log['holding_days'] = (trade_log['exit_date'] - trade_log['entry_date']).dt.days
            trade_log['return_pct'] = (trade_log['pnl'] / (trade_log['entry_price'] * trade_log['position'])) * 100
            return trade_log
        else:
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"❌ Backtest failed for {symbol}: {str(e)}")
        return pd.DataFrame()