import pandas as pd
from predict import predict_usage_risk
import os
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ml-batch")

def batch_score():
    base_path = os.path.dirname(__file__)
    features_path = os.path.join(base_path, "features.csv")
    
    if not os.path.exists(features_path):
        logger.error(f"Features file not found at {features_path}. Run feature_engineering.py first.")
        return

    logger.info(f"Loading features from {features_path}...")
    
    predictions = []
    for _, row in df.iterrows():
        features = {
            "avg_usage": row['avg_usage'],
            "growth_rate": row['growth_rate'],
            "variability": row['variability'],
            "peak_ratio": row['peak_ratio']
        }
        
        res = predict_usage_risk(features)
        predictions.append({
            "region": row['region'],
            "predicted_risk": res['congestion_risk'],
            "score": res['score'],
            "anomaly": res['anomaly_flag']
        })
        
    results_df = pd.DataFrame(predictions)
    output_path = os.path.join(base_path, "batch_predictions.csv")
    results_df.to_csv(output_path, index=False)
    logger.info(f"Batch scoring complete. Results saved to {output_path}")

if __name__ == "__main__":
    batch_score()
