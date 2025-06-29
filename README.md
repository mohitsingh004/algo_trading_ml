# 🤖⚡ Algo Trading System — Python-Based AI Trading Bot 📈

Welcome to a modular, intelligent **Algorithmic Trading System** built using Python.  
This bot:
- 📊 Fetches real-time stock data from NSE using `yfinance`
- 🧠 Applies both traditional strategies & AI/ML models
- ⏱️ Backtests historical performance
- 📄 Logs trades and predictions to Google Sheets
- 💥 Ready for integration with live brokers like Zerodha, AliceBlue

> ⚠️ Educational Use Only – Use at your own risk.

---

## 🧠 Features

✅ Fetches OHLCV data via API  
✅ Supports technical strategies (e.g. MA crossover)  
✅ Plug-and-play ML models (LSTM, XGBoost, etc.)  
✅ Backtesting engine with returns/PnL calculation  
✅ Google Sheets logging  
✅ Modular & production-ready code  
✅ Easy to expand with broker APIs, alerts, or dashboards

---

## 📁 Project Structure

algo_trading_ml/
├── main.py # 🧠 Main pipeline controller
├── settings.py # ⚙️ Configs: stocks, intervals, API keys
├── requirements.txt # 📦 All dependencies listed here
├── credentials.json # 🔐 Google Sheets OAuth credentials
└── modules/
├── init.py
├── data_fetcher.py # 📥 Pulls stock data from yfinance
├── strategy.py # 📊 Trading strategies (e.g. MA crossover)
├── backtester.py # ⏱️ Evaluates strategy returns
├── ml_model.py # 🤖 Loads & runs ML model predictions
└── gsheet.py # 📄 Exports signals to Google Sheets


---

## ⚙️ Setup Instructions

### 1. Clone the Repo
git clone https://github.com/mohitsingh004/algo_trading_ml.git
cd algo_trading_ml

2. Set Up a Virtual Environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

3. Install Required Libraries
pip install -r requirements.txt

4. Set Up Google Sheets API
Go to Google Cloud Console

Enable Google Sheets API

Create a Service Account

Download credentials.json

Share your sheet with: your-service-account@project-id.iam.gserviceaccount.com

🔐 Add credentials.json to .gitignore and NEVER upload it publicly.



📦 Required Libraries
Library	Use
yfinance----	Fetch historical market data
pandas---	Data manipulation
numpy	----Numeric calculations
matplotli---Plotting (optional)
joblib	---ML model loading
scikit-learn	---Training and testing models
gspread	-----Google Sheets integration
oauth2client-----	Google API authentication
argparse-------	CLI arguments (optional)
datetime, os------	Date handling, file paths


🔖 requirements.txt
yfinance==0.2.33
pandas==2.2.2
numpy==1.26.4
joblib==1.4.0
scikit-learn==1.5.0
matplotlib==3.9.0
gspread==6.0.2
oauth2client==4.1.3



🧩 How It Works
🔁 main.py
Entry point of the bot

Loads config, runs strategy, logs results

📥 data_fetcher.py
Uses yfinance to pull historical OHLCV data

📊 strategy.py
Implements technical indicators like MA crossover

⏱️ backtester.py
Simulates the strategy on historical data and returns metrics

🤖 ml_model.py
Loads ML model from .pkl file and makes predictions

📄 gsheet.py
Connects to your Google Sheet and pushes data

