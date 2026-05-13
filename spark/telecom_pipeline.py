import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, DoubleType, TimestampType, StringType
from pyspark.sql.functions import (
    to_timestamp, col, when, isnull, broadcast, 
    hour, date_format, sum as _sum, count as _count, desc
)

def create_session():
    """Task 2.7: Initialize SparkSession"""
    return SparkSession.builder \
        .appName("TelecomNetworkIntelligence") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

def load(spark):
    """Task 2.1: Distributed Ingestion"""
    schema = StructType([
        StructField("datetime", StringType(), True),
        StructField("CellID", IntegerType(), True),
        StructField("countrycode", IntegerType(), True),
        StructField("smsin", DoubleType(), True),
        StructField("smsout", DoubleType(), True),
        StructField("callin", DoubleType(), True),
        StructField("callout", DoubleType(), True),
        StructField("internet", DoubleType(), True)
    ])
    
    raw_path = "data/raw/*.csv"
    print(f"Loading data from {raw_path}...")
    return spark.read.format("csv") \
        .option("header", "true") \
        .schema(schema) \
        .load(raw_path)

def clean(df):
    """Task 2.2: Cleaning & Standardization"""
    print("Cleaning and standardizing data...")
    
    # 1. Rename columns to snake_case and unify counts (Normalization)
    # 2. Cast timestamp
    from pyspark.sql.functions import coalesce, lit
    
    cleaned_df = df.withColumn("timestamp", to_timestamp(col("datetime"), "yyyy-MM-dd HH:mm:ss")) \
        .withColumn("sms_count", coalesce(col("smsin"), lit(0)) + coalesce(col("smsout"), lit(0))) \
        .withColumn("call_count", coalesce(col("callin"), lit(0)) + coalesce(col("callout"), lit(0))) \
        .withColumnRenamed("CellID", "grid_id") \
        .withColumnRenamed("internet", "internet_usage") \
        .select("timestamp", "grid_id", "countrycode", "sms_count", "call_count", "internet_usage")
    
    # 3. Filter out invalid rows
    # Filter: internet_usage < 0 OR call_count is null
    cleaned_df = cleaned_df.filter(
        (col("internet_usage") >= 0) & 
        (~isnull(col("call_count")))
    )
    
    return cleaned_df

def enrich(df, spark):
    """Task 2.4: Joins with Geo Metadata"""
    print("Enriching with region mapping...")
    
    geo_path = "data/region_mapping.csv"
    geo_df = spark.read.csv(geo_path, header=True, inferSchema=True)
    
    # Use Broadcast Join because geo_df (region_mapping) is small (metadata).
    # This avoids a full shuffle of the large usage dataset.
    enriched_df = df.join(broadcast(geo_df), on="grid_id", how="left")
    
    return enriched_df

def aggregate(df):
    """Task 2.3: Aggregations"""
    print("Computing KPIs...")
    
    # Add helper columns for grouping
    df_with_time = df.withColumn("hour", hour(col("timestamp"))) \
                     .withColumn("date", date_format(col("timestamp"), "yyyy-MM-dd"))
    
    # 1. Calls per hour (across all regions)
    calls_per_hour = df_with_time.groupBy("hour").agg(_sum("call_count").alias("total_calls"))
    
    # 2. SMS per region per day
    sms_per_region_day = df_with_time.groupBy("region_name", "date").agg(_sum("sms_count").alias("total_sms"))
    
    # 3. Internet usage per day
    internet_per_day = df_with_time.groupBy("date").agg(_sum("internet_usage").alias("total_internet"))
    
    # 4. Top 5 peak usage hours (based on total activity: sms + call + internet)
    # Note: Normalizing weights might be needed, but here we sum raw counts for simplicity
    peak_hours = df_with_time.groupBy("hour").agg(
        (_sum("sms_count") + _sum("call_count") + _sum("internet_usage")).alias("total_activity")
    ).orderBy(desc("total_activity")).limit(5)
    
    # Summary dictionary for writing
    summary = {
        "calls_per_hour": calls_per_hour,
        "sms_per_region_day": sms_per_region_day,
        "internet_per_day": internet_per_day,
        "peak_hours": peak_hours
    }
    
    return summary

def optimize_and_debug(df):
    """Task 2.5: Performance Optimization"""
    print("\n--- Optimization & Plan Analysis ---")
    
    # 1. Column Pruning: Already handled in clean() and select() steps
    # 2. Caching: Caching the enriched dataset as it is the base for multiple aggregations
    optimized_df = df.cache()
    
    # 3. Repartitioning: Repartition by grid_id to optimize downstream joins/groups
    optimized_df = optimized_df.repartition(4, "grid_id")
    
    # Capture explain() output
    print("Execution Plan (Physical):")
    optimized_df.explain()
    
    return optimized_df

def write(df, summary):
    """Task 2.6: Write Processed Output"""
    print("Writing processed outputs...")
    
    # Add partition column
    df_to_write = df.withColumn("date_partition", date_format(col("timestamp"), "yyyy-MM-dd"))
    
    # 1. Cleaned dataset to Parquet, partitioned by date
    processed_path = "data/processed/usage_cleaned"
    df_to_write.write.mode("overwrite").partitionBy("date_partition").parquet(processed_path)
    print(f"Cleaned data saved to {processed_path}")
    
    # 2. Summary aggregations
    summary_base_path = "data/processed/summaries"
    for name, s_df in summary.items():
        path = os.path.join(summary_base_path, name)
        s_df.coalesce(1).write.mode("overwrite").csv(path, header=True)
        print(f"Summary '{name}' saved to {path}")

def main():
    """Task 2.7: Main Entry Point"""
    # Create session
    spark = create_session()
    
    try:
        # Load
        raw_df = load(spark)
        
        # Clean
        cleaned_df = clean(raw_df)
        
        # Enrich
        enriched_df = enrich(cleaned_df, spark)
        
        # Optimize
        optimized_df = optimize_and_debug(enriched_df)
        
        # Aggregate
        summary = aggregate(optimized_df)
        
        # Write
        write(optimized_df, summary)
        
        print("\nPipeline execution complete.")
        
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
