import gspread
import numpy as np
import pandas as pd
import logging
from oauth2client.service_account import ServiceAccountCredentials

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_to_serializable(value):
    """Convert numpy types to native Python types for Google Sheets"""
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64)):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif pd.isna(value):
        return ""
    elif isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d')
    else:
        return value

def get_sheet_client(spreadsheet_id):
    """Authenticate and access Google Sheet"""
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(spreadsheet_id)
        
        # Debug logging
        logging.info(f"✅ Accessed spreadsheet: {sheet.title}")
        logging.info(f"📊 Worksheets: {[ws.title for ws in sheet.worksheets()]}")
        
        return sheet
    except gspread.SpreadsheetNotFound:
        logging.error(f"❌ Spreadsheet not found with ID: {spreadsheet_id}")
        return None
    except Exception as e:
        logging.error(f"❌ Google Sheets authentication failed: {str(e)}")
        return None

def create_worksheet_if_not_exists(sheet, title, headers):
    """Create worksheet if it doesn't exist"""
    try:
        return sheet.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        logging.info(f"Creating new worksheet: {title}")
        try:
            worksheet = sheet.add_worksheet(title=title, rows=1000, cols=len(headers))
            worksheet.append_row(headers)
            logging.info(f"✅ Created new worksheet: {title}")
            return worksheet
        except Exception as e:
            logging.error(f"❌ Failed to create worksheet {title}: {str(e)}")
            return None
    except Exception as e:
        logging.error(f"❌ Error accessing worksheet {title}: {str(e)}")
        return None

def log_trades_to_sheet(trade_df, symbol, spreadsheet_id):
    """Log trades to Google Sheet with proper serialization"""
    try:
        logging.info(f"📤 Preparing to upload {len(trade_df)} trades for {symbol}")
        sheet = get_sheet_client(spreadsheet_id)
        if not sheet:
            return
            
        # Define headers
        trade_headers = [
            'entry_date', 'entry_price', 'position', 'exit_date',
            'exit_price', 'pnl', 'symbol', 'holding_days', 'return_pct'
        ]
        
        # Create worksheet if needed
        worksheet = create_worksheet_if_not_exists(sheet, "TradeLog", trade_headers)
        if not worksheet:
            return
            
        # Prepare data with serialization
        data = []
        for _, row in trade_df.iterrows():
            if all(col in row for col in trade_headers):
                data.append([convert_to_serializable(row[col]) for col in trade_headers])
        
        # Append new trades
        if data:
            current_row_count = len(worksheet.get_all_values())
            worksheet.append_rows(data)
            new_row_count = len(worksheet.get_all_values())
            added_rows = new_row_count - current_row_count
            logging.info(f"✅ Uploaded {added_rows} trades for {symbol} to Google Sheets")
            logging.info(f"📝 Total rows in TradeLog: {new_row_count}")
        else:
            logging.warning("⚠️ No trade data to upload")
    except Exception as e:
        logging.error(f"❌ Failed to log trades for {symbol}: {str(e)}")

def log_summary_to_sheet(summary_df, spreadsheet_id):
    """Log summary to Google Sheet with proper serialization"""
    try:
        logging.info("📤 Preparing to upload summary")
        sheet = get_sheet_client(spreadsheet_id)
        if not sheet:
            return
            
        # Prepare summary stats
        stats = {
            "Total Trades": len(summary_df),
            "Winning Trades": (summary_df['pnl'] > 0).sum() if 'pnl' in summary_df else 0,
            "Losing Trades": (summary_df['pnl'] < 0).sum() if 'pnl' in summary_df else 0,
            "Win Ratio": f"{(summary_df['pnl'] > 0).mean():.2%}" if 'pnl' in summary_df else "0.00%",
            "Average P&L": summary_df['pnl'].mean() if 'pnl' in summary_df else 0,
            "Total P&L": summary_df['pnl'].sum() if 'pnl' in summary_df else 0,
            "Best Trade": summary_df['pnl'].max() if 'pnl' in summary_df else 0,
            "Worst Trade": summary_df['pnl'].min() if 'pnl' in summary_df else 0
        }
        
        # Convert to serializable format
        serializable_stats = {k: convert_to_serializable(v) for k, v in stats.items()}
        
        # Format as rows
        data = [["Metric", "Value"]]
        data.extend([[k, v] for k, v in serializable_stats.items()])
        
        # Log the data being sent
        logging.info(f"📋 Summary data: {data}")
        
        # Create or get worksheet
        summary_headers = ["Metric", "Value"]
        worksheet = create_worksheet_if_not_exists(sheet, "Summary", summary_headers)
        if not worksheet:
            return
            
        # Clear and update
        worksheet.clear()
        worksheet.update('A1', data)
        logging.info("✅ Uploaded summary to Google Sheets")
        
        # Verify update
        updated_data = worksheet.get_all_values()
        logging.info(f"📝 Summary worksheet now has {len(updated_data)} rows")
    except Exception as e:
        logging.error(f"❌ Failed to log summary: {str(e)}")

def log_model_accuracy(symbol, accuracy, spreadsheet_id):
    """Log ML accuracy to Google Sheet"""
    try:
        logging.info(f"📤 Preparing to upload ML accuracy for {symbol}")
        sheet = get_sheet_client(spreadsheet_id)
        if not sheet:
            return
            
        # Create or get worksheet
        ml_headers = ["Symbol", "Accuracy"]
        worksheet = create_worksheet_if_not_exists(sheet, "MLResults", ml_headers)
        if not worksheet:
            return
            
        # Append new row
        row_data = [symbol, f"{accuracy:.2%}"]
        current_row_count = len(worksheet.get_all_values())
        worksheet.append_row(row_data)
        new_row_count = len(worksheet.get_all_values())
        
        # Verify addition
        if new_row_count > current_row_count:
            logging.info(f"✅ Uploaded ML accuracy for {symbol} to Google Sheets")
            logging.info(f"📝 Total rows in MLResults: {new_row_count}")
        else:
            logging.warning("⚠️ ML accuracy row not added")
    except Exception as e:
        logging.error(f"❌ Failed to log ML accuracy for {symbol}: {str(e)}")