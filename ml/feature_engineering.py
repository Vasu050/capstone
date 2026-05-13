import os
import logging
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import numpy as np

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ml-features")

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

def generate_features():
    conn = get_connection()
    try:
        query = """
            SELECT r.region_name, t.hour, f.internet_mb, f.call_count, f.sms_count
            FROM fact_usage f
            JOIN dim_region r ON f.region_id = r.region_id
            JOIN dim_time t ON f.time_id = t.time_id
        """
        df = pd.read_sql(query, conn)
        
        # Calculate region-level stats for relative comparisons
        region_stats = df.groupby('region_name')['internet_mb'].agg(['mean', 'std', 'max']).reset_index()
        region_stats.columns = ['region_name', 'reg_avg', 'reg_std', 'reg_max']
        
        df = df.merge(region_stats, on='region_name')
        
        # Create features per row (per region per hour)
        features_list = []
        for _, row in df.iterrows():
            avg_usage = row['reg_avg']
            # Variability per row is just distance from mean
            variability = abs(row['internet_mb'] - avg_usage)
            peak_ratio = row['internet_mb'] / avg_usage if avg_usage > 0 else 0
            
            # Growth rate (mocking variation)
            growth_rate = 0.02 + (0.1 * (row['hour'] / 24)) 
            
            features_list.append({
                'region': row['region_name'],
                'hour': row['hour'],
                'avg_usage': row['internet_mb'], # Current usage as "avg" for this sample
                'growth_rate': growth_rate,
                'variability': variability,
                'peak_ratio': peak_ratio,
                'actual_usage': row['internet_mb'],
                'reg_max': row['reg_max']
            })
            
        features_df = pd.DataFrame(features_list)
        
        # Labelling rules (Task 6.1) based on the full distribution of usage
        # We use the actual usage in that hour compared to the global distribution
        p90 = features_df['actual_usage'].quantile(0.9)
        p70 = features_df['actual_usage'].quantile(0.7)
        
        def label_risk(val):
            if val >= p90: return 'HIGH'
            if val >= p70: return 'MEDIUM'
            return 'LOW'
            
        features_df['congestion_risk'] = features_df['actual_usage'].apply(label_risk)
        
        # Clean data
        features_df = features_df.replace([np.inf, -np.inf], np.nan).fillna(0)
        
        os.makedirs("ml", exist_ok=True)
        features_df.to_csv("ml/features.csv", index=False)
        logger.info(f"Feature engineering complete. Generated {len(features_df)} samples.")
        return features_df
        
    finally:
        conn.close()

if __name__ == "__main__":
    generate_features()
