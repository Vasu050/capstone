import joblib
import pandas as pd
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

def predict_usage_risk(features: dict) -> dict:
    """
    Predict congestion risk based on input features.
    Expected features: ['avg_usage', 'growth_rate', 'variability', 'peak_ratio']
    """
    if not os.path.exists(MODEL_PATH):
        return {
            "congestion_risk": "UNKNOWN",
            "anomaly_flag": False,
            "score": 0.0,
            "error": "Model not trained"
        }

    # Load model
    model = joblib.load(MODEL_PATH)
    
    # Prepare data
    input_df = pd.DataFrame([features])
    
    # Required columns
    cols = ['avg_usage', 'growth_rate', 'variability', 'peak_ratio']
    # Ensure all columns exist (fill with 0 if missing)
    for col in cols:
        if col not in input_df.columns:
            input_df[col] = 0.0
            
    input_df = input_df[cols]
    
    # Predict
    risk = model.predict(input_df)[0]
    probs = model.predict_proba(input_df)[0]
    score = float(max(probs))
    
    # Anomaly detection (rule-based)
    # If variability is 3x higher than average, flag as anomaly
    anomaly = features.get('variability', 0) > (features.get('avg_usage', 0) * 0.5)
    
    return {
        "congestion_risk": risk,
        "anomaly_flag": bool(anomaly),
        "score": score
    }

if __name__ == "__main__":
    # Test prediction
    test_features = {
        "avg_usage": 1500.0,
        "growth_rate": 0.15,
        "variability": 300.0,
        "peak_ratio": 1.5
    }
    print(predict_usage_risk(test_features))
