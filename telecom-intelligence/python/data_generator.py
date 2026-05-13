import os
import csv
from datetime import datetime, timedelta

def generate_sample_data():
    # Use the path relative to the root or absolute
    base_dir = r"data\raw"
    os.makedirs(base_dir, exist_ok=True)
    
    # Generate 3 partition files to test distributed ingestion
    for i in range(1, 4):
        file_path = os.path.join(base_dir, f"telecom_data_part_{i}.csv")
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            # Schema: datetime, CellID, countrycode, smsin, smsout, callin, callout, internet
            writer.writerow(['datetime', 'CellID', 'countrycode', 'smsin', 'smsout', 'callin', 'callout', 'internet'])
            
            start_time = datetime(2026, 5, 1, 10, 0, 0)
            for j in range(15): # 15 records per file
                row_time = (start_time + timedelta(hours=j)).strftime('%Y-%m-%d %H:%M:%S')
                writer.writerow([
                    row_time,
                    1000 + i, # grid_id
                    39,       # countrycode
                    0.5 * j,  # smsin
                    0.2 * j,  # smsout
                    1.0 * j,  # callin
                    0.8 * j,  # callout
                    100.5 * j # internet
                ])
        print(f"Generated: {file_path}")

if __name__ == "__main__":
    generate_sample_data()
