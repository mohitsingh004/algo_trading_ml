# test_upload.py
from modules.gsheet import update_sheet_from_df
import pandas as pd

# Sample data to upload
df = pd.DataFrame({
    "Symbol": ["RELIANCE.NS", "TCS.NS"],
    "Price": [2800, 3200],
    "Signal": ["Buy", "Hold"]
})

# Replace with your actual Google Sheet ID
SPREADSHEET_ID = "your-spreadsheet-1OJW19vsYGIj-ZEHvuF5G1hEPqmNixC3VUhEIQ9eMQaw"

# Upload to Google Sheet
update_sheet_from_df(df, "Test_Upload",'1OJW19vsYGIj-ZEHvuF5G1hEPqmNixC3VUhEIQ9eMQaw')