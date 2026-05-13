import os
import pandas as pd
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

# Load environment variables from project root
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD")
    )

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    db_name = os.getenv("MYSQL_DATABASE")
    
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Read and execute schema.sql
        schema_path = os.path.join("warehouse", "schema.sql")
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            
        # Execute each statement
        for statement in schema_sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
        
        print(f"Database '{db_name}' and tables initialized.")
        conn.commit()
    except Error as e:
        print(f"Error setting up database: {e}")
    finally:
        cursor.close()
        conn.close()

def load_data():
    db_name = os.getenv("MYSQL_DATABASE")
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=db_name
    )
    cursor = conn.cursor()
    
    try:
        # 1. Read processed Parquet files
        processed_path = os.path.join("data", "processed", "usage_cleaned")
        # Find all parquet files in partitions
        parquet_files = []
        for root, dirs, files in os.walk(processed_path):
            for file in files:
                if file.endswith(".parquet"):
                    parquet_files.append(os.path.join(root, file))
        
        if not parquet_files:
            print("No processed Parquet files found.")
            return

        df = pd.concat([pd.read_parquet(f) for f in parquet_files])
        print(f"Loaded {len(df)} records from Parquet.")

        # 2. Populate dim_time
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['time_id'] = df['timestamp'].dt.strftime('%Y%m%d%H').astype(int)
        
        dim_time = df[['time_id', 'timestamp']].copy()
        dim_time['date'] = dim_time['timestamp'].dt.date
        dim_time['hour'] = dim_time['timestamp'].dt.hour
        dim_time['day'] = dim_time['timestamp'].dt.day
        dim_time['month'] = dim_time['timestamp'].dt.month
        dim_time['weekday'] = dim_time['timestamp'].dt.day_name()
        
        dim_time_unique = dim_time.drop(columns=['timestamp']).drop_duplicates()
        
        for _, row in dim_time_unique.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO dim_time (time_id, date, hour, day, month, weekday)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, tuple(row))

        # 3. Populate dim_region
        # Note: We assume region_mapping.csv has the source metadata
        region_df = pd.read_csv(os.path.join("data", "region_mapping.csv"))
        for _, row in region_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO dim_region (region_id, region_name, city)
                VALUES (%s, %s, %s)
            """, (int(row['grid_id']), row['region_name'], row['city']))

        # 4. Populate fact_usage
        fact_df = df[['time_id', 'grid_id', 'call_count', 'sms_count', 'internet_usage']].copy()
        fact_df = fact_df.rename(columns={'grid_id': 'region_id', 'internet_usage': 'internet_mb'})
        
        for _, row in fact_df.iterrows():
            cursor.execute("""
                INSERT INTO fact_usage (time_id, region_id, call_count, sms_count, internet_mb)
                VALUES (%s, %s, %s, %s, %s)
            """, (int(row['time_id']), int(row['region_id']), int(row['call_count']), int(row['sms_count']), float(row['internet_mb'])))

        conn.commit()
        print("Warehouse loading complete.")
        
    except Exception as e:
        print(f"Error loading warehouse: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
    load_data()
