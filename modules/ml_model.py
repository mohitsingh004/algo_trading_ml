from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def prepare_features(df):
    """Prepare features for ML model with robust handling"""
    try:
        # Basic features
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(window=14).std()
        
        # Momentum features
        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        
        # Volume features
        df['volume_change'] = df['volume'] / df['volume'].shift(1) - 1
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        
        # Ensure required indicators exist
        for col in ['rsi', 'macd', 'signal', 'ma20', 'ma50']:
            if col not in df.columns:
                df[col] = 0
        
        # Target: 1 if next day return > 0.5%, else 0
        df['target'] = (df['close'].shift(-1) > df['close'] * 1.005).astype(int)
        
        # Drop rows with missing values
        df = df.dropna()
        
        return df
    except Exception as e:
        logging.error(f"❌ Feature preparation failed: {str(e)}")
        return pd.DataFrame()

def train_model(df):
    """Train and evaluate ML model with validation"""
    try:
        if df.empty or 'target' not in df.columns or len(df) < 100:
            logging.warning("⚠️ Insufficient data for training")
            return None, 0.0
        
        # Feature selection
        features = [
            'rsi', 'macd', 'signal', 'ma20', 'ma50', 
            'returns', 'volatility', 'momentum_5', 'volume_change'
        ]
        
        # Ensure we have required features
        available_features = [f for f in features if f in df.columns]
        if len(available_features) < 5:
            logging.warning(f"⚠️ Only {len(available_features)} features available")
            return None, 0.0
        
        X = df[available_features]
        y = df['target']
        
        # Handle class imbalance
        class_ratio = y.mean()
        if class_ratio < 0.3 or class_ratio > 0.7:
            class_weight = 'balanced'
        else:
            class_weight = None
        
        # Chronological split
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Handle small datasets
        if len(X_train) < 50 or len(X_test) < 10:
            logging.warning("⚠️ Insufficient data for train/test split")
            return None, 0.0
        
        # Train model
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight=class_weight,
            min_samples_split=5
        )
        
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        
        # Validate accuracy
        if accuracy < 0.45 or accuracy > 0.95:  # Sanity check
            logging.warning(f"⚠️ Questionable accuracy: {accuracy:.2%}")
            return model, 0.0
        
        return model, accuracy
    except Exception as e:
        logging.error(f"❌ Model training failed: {str(e)}")
        return None, 0.0