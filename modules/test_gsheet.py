from modules.gsheet import get_sheet_client

SPREADSHEET_ID = '1OJW19vsYGIj-ZEHvuF5G1hEPqmNixC3VUhEIQ9eMQaw'

sheet = get_sheet_client(SPREADSHEET_ID)
if sheet:
    print(f"Sheet Title: {sheet.title}")
    print("Worksheets:", [ws.title for ws in sheet.worksheets()])
    
    # Check TradeLog
    trade_log = sheet.worksheet("TradeLog")
    print(f"TradeLog rows: {len(trade_log.get_all_values())}")
    
    # Check Summary
    summary = sheet.worksheet("Summary")
    print("Summary data:", summary.get_all_values())
    
    # Check MLResults
    ml_results = sheet.worksheet("MLResults")
    print("ML Results:", ml_results.get_all_values())
else:
    print("Failed to access sheet")