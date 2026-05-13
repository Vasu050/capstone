import pandas as pd
import numpy as np

class UsageProcessor:
    def __init__(self):
        self.df = None

    def load_data(self, path):
        """
        Load CSV into a DataFrame.
        Expected columns: datetime, CellID, countrycode, smsin, smsout, callin, callout, internet
        """
        try:
            self.df = pd.read_csv(path)
            print(f"Successfully loaded data from {path}")
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def clean_data(self):
        """
        Cleans the loaded data:
        - Converts timestamp to datetime
        - Extracts hour and day
        - Drops invalid (negative) rows
        - Ensures numeric usage fields
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # 1. Standardize column mapping & Handle Missing Values
        # Note: We aggregate sms and call counts as they are often split into incoming/outgoing
        self.df['sms_count'] = self.df['smsin'].fillna(0) + self.df['smsout'].fillna(0)
        self.df['call_count'] = self.df['callin'].fillna(0) + self.df['callout'].fillna(0)
        self.df = self.df.rename(columns={
            'datetime': 'timestamp',
            'CellID': 'grid_id',
            'internet': 'internet_usage'
        })

        # 2. Convert to datetime and extract features
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['day'] = self.df['timestamp'].dt.day

        # 3. Ensure numeric usage fields
        usage_cols = ['sms_count', 'call_count', 'internet_usage']
        for col in usage_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

        # 4. Drop invalid rows (negative values)
        initial_count = len(self.df)
        self.df = self.df[
            (self.df['sms_count'] >= 0) & 
            (self.df['call_count'] >= 0) & 
            (self.df['internet_usage'] >= 0)
        ]
        
        # Drop rows with missing essential identifiers
        self.df = self.df.dropna(subset=['timestamp', 'grid_id'])
        
        final_count = len(self.df)
        print(f"Cleaning complete. Removed {initial_count - final_count} invalid rows.")

    def compute_daily_usage(self):
        """
        Computes total usage per day.
        """
        if self.df is None:
            raise ValueError("Data not loaded or cleaned.")

        daily_usage = self.df.groupby('day')[['sms_count', 'call_count', 'internet_usage']].sum()
        return daily_usage

    def compute_kpis(self):
        """
        Computes Key Performance Indicators:
        - Total usage per region (grid_id)
        - Average usage per hour
        - Peak usage hour
        """
        if self.df is None:
            raise ValueError("Data not loaded or cleaned.")

        # 1. Total usage per region
        usage_per_region = self.df.groupby('grid_id')[['sms_count', 'call_count', 'internet_usage']].sum()

        # 2. Average usage per hour
        avg_usage_per_hour = self.df.groupby('hour')[['sms_count', 'call_count', 'internet_usage']].mean()

        # 3. Peak usage hour (based on internet_usage)
        hourly_total = self.df.groupby('hour')['internet_usage'].sum()
        peak_hour = hourly_total.idxmax()
        peak_value = hourly_total.max()

        kpis = {
            'usage_per_region': usage_per_region,
            'avg_usage_per_hour': avg_usage_per_hour,
            'peak_usage_hour': peak_hour,
            'peak_usage_value': peak_value
        }

        return kpis

def call_plan_api(customer_id):
    """
    Task 1.3: Simulates calling GET /plans/customer/{id}.
    Returns a mock JSON response.
    """
    # Mock data for demonstration
    mock_responses = {
        101: {"customer_id": 101, "plan_name": "Premium Data", "monthly_limit_gb": 50, "status": "active"},
        102: {"customer_id": 102, "plan_name": "Basic Voice", "monthly_limit_gb": 5, "status": "active"},
        103: {"customer_id": 103, "plan_name": "Unlimited Social", "monthly_limit_gb": 100, "status": "expired"}
    }
    
    # Return the mock response or a default if ID not found
    return mock_responses.get(customer_id, {"customer_id": customer_id, "plan_name": "Standard", "monthly_limit_gb": 10, "status": "unknown"})
