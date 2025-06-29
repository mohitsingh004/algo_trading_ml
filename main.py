import pandas as pd
import os
import logging
import time
import numpy as np

# Import settings directly
SPREADSHEET_ID = '1OJW19vsYGIj-ZEHvuF5G1hEPqmNixC3VUhEIQ9eMQaw'
NIFTY_50 = ['TATAMOTORS.NS', 'ADANIENT.NS', 'HINDALCO.NS', 'JSWSTEEL.NS', 'SBIN.NS']
INITIAL_CAPITAL = 100000

# Import modules
from modules.data_fetcher import fetch_data
from modules.strategy import calculate_indicators, generate_signals
from modules.backtester import backtest_strategy
from modules.ml_model import prepare_features, train_model
from modules.gsheet import log_trades_to_sheet, log_summary_to_sheet, log_model_accuracy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trading_system.log"),
        logging.StreamHandler()
    ]
)

def run_strategy():
    all_trades = []
    os.makedirs("data", exist_ok=True)
    start_time = time.time()

    logging.info("🚀 Starting Algo-Trading System")
    logging.info(f"📊 Processing {len(NIFTY_50)} stocks: {', '.join(NIFTY_50)}")

    for i, symbol in enumerate(NIFTY_50):
        symbol_start = time.time()
        try:
            logging.info(f"\n{'='*50}")
            logging.info(f"🚀 Processing {symbol} ({i+1}/{len(NIFTY_50)})")
            logging.info(f"{'='*50}")

            # 1. Fetch data with extended history
            df = fetch_data(symbol, period="5y")
            if df.empty or len(df) < 200:
                logging.warning(f"⚠️ Insufficient data for {symbol}. Skipping.")
                continue
                
            logging.info(f"📊 Data shape: {df.shape} | From {df.index[0].date()} to {df.index[-1].date()}")

            # 2. Calculate indicators
            df = calculate_indicators(df)
            
            # 3. Generate signals
            signal_df = generate_signals(df.copy())
            
            # Debug: Show signal stats
            logging.info(f"🔍 Signals - Buy: {signal_df['buy_signal'].sum()}, Sell: {signal_df['sell_signal'].sum()}")
            logging.info(f"📈 Indicators - RSI min: {signal_df['rsi'].min():.2f}, max: {signal_df['rsi'].max():.2f}")
            
            # 4. Backtest with sufficient history
            min_history = max(126, int(len(signal_df) * 0.3))
            backtest_df = signal_df.iloc[-min_history:] 
            logging.info(f"💼 Backtesting last {len(backtest_df)} days")
            
            trade_df = backtest_strategy(backtest_df, symbol, INITIAL_CAPITAL)
            
            # 5. Process trades
            if not trade_df.empty:
                all_trades.append(trade_df)
                output_path = f"data/{symbol}_trades.csv"
                trade_df.to_csv(output_path, index=False)
                logging.info(f"💾 Saved {len(trade_df)} trades to {output_path}")
                
                # Upload to Google Sheet
                log_trades_to_sheet(trade_df, symbol, SPREADSHEET_ID)
                
                # Calculate performance
                if 'pnl' in trade_df.columns:
                    win_rate = (trade_df['pnl'] > 0).mean()
                    avg_return = trade_df['return_pct'].mean() if 'return_pct' in trade_df.columns else 0
                    logging.info(f"📈 Performance | Win Rate: {win_rate:.2%} | Avg Return: {avg_return:.2f}%")
            else:
                logging.warning(f"⚠️ No trades executed for {symbol}")
                
                # Debug signals in backtest period
                buy_signals = backtest_df['buy_signal'].sum()
                sell_signals = backtest_df['sell_signal'].sum()
                logging.info(f"🔍 Signals in period - Buy: {buy_signals}, Sell: {sell_signals}")

            # 6. ML Preparation
            ml_df = prepare_features(df.copy())
            
            # 7. Train ML model
            if not ml_df.empty and 'target' in ml_df.columns:
                model, accuracy = train_model(ml_df)
                if accuracy > 0.45:
                    logging.info(f"🤖 Model Accuracy: {accuracy:.2%}")
                    log_model_accuracy(symbol, accuracy, SPREADSHEET_ID)
                else:
                    logging.warning("⚠️ Low accuracy, skipping upload")
            else:
                logging.warning("⚠️ Insufficient data for ML")
                
            # 8. Time management
            symbol_time = time.time() - symbol_start
            logging.info(f"⏱️ Processed in {symbol_time:.2f}s")
            
            # Add delay between stocks
            if i < len(NIFTY_50) - 1:
                delay = max(3, 6 - symbol_time)
                logging.info(f"⏳ Waiting {delay:.1f}s before next symbol...")
                time.sleep(delay)
                
        except Exception as e:
            logging.error(f"❌ Error processing {symbol}: {str(e)}")
            continue

    # 9. Final summary
    logging.info("\n" + "="*50)
    logging.info("📊 Generating summary report")
    logging.info("="*50)
    
    if all_trades:
        final_df = pd.concat(all_trades, ignore_index=True)
        summary_path = "data/all_trades_summary.csv"
        final_df.to_csv(summary_path, index=False)
        
        # Calculate performance
        total_trades = len(final_df)
        win_rate = (final_df['pnl'] > 0).mean() if 'pnl' in final_df.columns else 0
        avg_return = final_df['return_pct'].mean() if 'return_pct' in final_df.columns else 0
        total_pnl = final_df['pnl'].sum() if 'pnl' in final_df.columns else 0
        
        logging.info(f"✅ Saved {total_trades} trades to {summary_path}")
        logging.info(f"📈 Summary | Win Rate: {win_rate:.2%} | Avg Return: {avg_return:.2f}% | Total P&L: ₹{total_pnl:,.2f}")
        
        # Upload summary
        log_summary_to_sheet(final_df, SPREADSHEET_ID)
    else:
        logging.warning("⚠️ No trades executed")

    # Final stats
    total_time = time.time() - start_time
    logging.info(f"\n{'='*50}")
    logging.info(f"🏁 Completed in {total_time:.2f}s | Processed {len(NIFTY_50)} stocks")
    logging.info("="*50)

if __name__ == "__main__":
    run_strategy()