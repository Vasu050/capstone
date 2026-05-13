# Telecom Network Intelligence System — Design Document

This document outlines the architectural decisions, storage strategies, and operational characteristics of the system.

## Task 3.3 — Batch vs Streaming Decision

| Data Flow | Classification | Rationale |
| :--- | :--- | :--- |
| Network activity logs from cell towers | **Streaming** | High volume, continuous data that requires real-time monitoring for immediate issue detection. |
| Daily usage summary | **Batch** | Processed once a day for reporting and trend analysis; doesn't require sub-second latency. |
| Monthly billing reports | **Batch** | Generated on a fixed schedule (monthly) based on a complete set of historical records. |
| Network congestion alerts | **Streaming** | Critical for operational response; must be detected and alerted as soon as thresholds are hit. |
| Customer dashboard data | **Batch/Hybrid** | Usually refreshed periodically (e.g., hourly) as users typically look for trends rather than live streams. |

---

## Task 3.5 — Storage Strategy

### Raw Layer — Why CSV?
- **Universal Format**: CSV is the most common format for logs produced by legacy network equipment and cell towers.
- **Interoperability**: Easy to ingest using any tool (Spark, Python, Airflow) without complex serialisation libraries.

### Processed Layer — Why Parquet?
- **Columnar Storage**: Optimized for analytical queries (OLAP) which typically read a subset of columns.
- **Compression**: Parquet provides excellent compression ratios, reducing storage costs significantly compared to CSV.
- **Partitioning**: By partitioning by **date**, we enable "Partition Pruning"—Spark only reads the specific day's data required for a query, drastically improving performance.

### Warehouse Layer — Why Star Schema?
- **Performance**: Minimizes joins for complex analytical queries. 
- **Simplicity**: Users (and BI tools) can easily understand the relationship between facts (usage metrics) and dimensions (time, region).
- **Storage Efficiency**: Normalizing dimensions like `dim_region` avoids repeating long strings (region names, cities) millions of times in the fact table.

---

## Task 3.6 — Failure Handling

The pipeline handles failures at the `validate_files` and `move_files` stages:
1.  **Missing Input**: `detect_files` logs that no files are found and the DAG gracefully finishes without error.
2.  **Corrupt Rows**: `validate_files` checks the schema and nulls. Any file failing these checks is moved to `data/rejected/`.
3.  **Duplicate Files**: Handled by the file system movement logic (shutil) and can be extended with checksum checks if needed.

---

## Phase 6 — Machine Learning Problem Statement

### Objective
The system predicts **Congestion Risk** (Low, Medium, High) for specific network regions based on historical usage patterns.

### Operational Value
Predicting congestion allows telecom operators to proactively rebalance network load, schedule maintenance, or temporarily increase capacity in high-risk areas, ensuring a consistent quality of service for customers and preventing outages.

### Data Labelling Strategy
As the dataset is unlabelled, we apply a rule-based labelling approach:
- **HIGH Risk**: Usage > 90th percentile of historical peak usage.
- **MEDIUM Risk**: Usage between 70th and 90th percentile.
- **LOW Risk**: Usage below the 70th percentile.
Anomalies are flagged if usage exceeds 3 standard deviations from the mean for that specific region.
