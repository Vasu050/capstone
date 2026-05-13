from fastapi import APIRouter, HTTPException
from api.database import get_db_connection
from api.schemas import UsageSummary, RegionUsage, PeakTraffic, HourlyUsage, PeakHour, PeakRegion, MLFeatures

router = APIRouter(prefix="/usage", tags=["Usage"])

@router.get("/summary", response_model=UsageSummary)
def get_usage_summary():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT SUM(call_count) as total_calls, SUM(sms_count) as total_sms, SUM(internet_mb) as total_internet_mb FROM fact_usage")
        totals = cursor.fetchone()
        
        cursor.execute("""
            SELECT hour FROM fact_usage f 
            JOIN dim_time t ON f.time_id = t.time_id 
            GROUP BY hour ORDER BY SUM(internet_mb) DESC LIMIT 1
        """)
        peak_hour_res = cursor.fetchone()
        peak_hour = peak_hour_res['hour'] if peak_hour_res else 0
        
        cursor.execute("""
            SELECT region_name FROM fact_usage f 
            JOIN dim_region r ON f.region_id = r.region_id 
            GROUP BY region_name ORDER BY SUM(internet_mb) DESC LIMIT 1
        """)
        busiest_reg_res = cursor.fetchone()
        busiest_region = busiest_reg_res['region_name'] if busiest_reg_res else "N/A"
        
        return UsageSummary(
            total_calls=totals['total_calls'] or 0,
            total_sms=totals['total_sms'] or 0,
            total_internet_mb=round(totals['total_internet_mb'] or 0.0, 2),
            peak_hour=peak_hour,
            busiest_region=busiest_region
        )
    finally:
        cursor.close()
        conn.close()

@router.get("/region/{region}", response_model=RegionUsage)
def get_region_usage(region: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT hour, SUM(call_count) as calls, SUM(sms_count) as sms, SUM(internet_mb) as internet_mb 
            FROM fact_usage f 
            JOIN dim_region r ON f.region_id = r.region_id 
            JOIN dim_time t ON f.time_id = t.time_id 
            WHERE r.region_name = %s 
            GROUP BY hour
            ORDER BY hour
        """
        cursor.execute(query, (region,))
        rows = cursor.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail=f"Region '{region}' not found")
            
        distribution = [HourlyUsage(
            hour=r['hour'], 
            calls=r['calls'], 
            sms=r['sms'], 
            internet_mb=round(r['internet_mb'], 2)
        ) for r in rows]
        
        return RegionUsage(region=region, hourly_distribution=distribution, trend=[round(r['internet_mb'], 2) for r in rows])
    finally:
        cursor.close()
        conn.close()

@router.get("/peak", response_model=PeakTraffic)
def get_peak_traffic():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT hour, SUM(internet_mb) as total_usage FROM fact_usage f JOIN dim_time t ON f.time_id = t.time_id GROUP BY hour ORDER BY total_usage DESC LIMIT 5")
        top_hours = [PeakHour(hour=r['hour'], total_usage=round(r['total_usage'], 2)) for r in cursor.fetchall()]
        
        cursor.execute("SELECT region_name as region, SUM(internet_mb) as total_usage FROM fact_usage f JOIN dim_region r ON f.region_id = r.region_id GROUP BY region_name ORDER BY total_usage DESC LIMIT 5")
        top_regions = [PeakRegion(region=r['region'], total_usage=round(r['total_usage'], 2)) for r in cursor.fetchall()]
        
        return PeakTraffic(top_hours=top_hours, top_regions=top_regions)
    finally:
        cursor.close()
        conn.close()

@router.get("/features/{region}", response_model=MLFeatures)
def get_ml_features(region: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT AVG(internet_mb) as avg_usage, STDDEV(internet_mb) as variability, MAX(internet_mb) as peak_usage FROM fact_usage f JOIN dim_region r ON f.region_id = r.region_id WHERE r.region_name = %s"
        cursor.execute(query, (region,))
        stats = cursor.fetchone()
        
        if not stats or stats['avg_usage'] is None:
            raise HTTPException(status_code=404, detail=f"No features available for region '{region}'")
            
        return MLFeatures(
            region=region,
            avg_usage=round(stats['avg_usage'], 2),
            growth_rate=0.05,
            variability=round(stats['variability'] or 0.0, 2),
            peak_ratio=round(stats['peak_usage'] / stats['avg_usage'], 2) if stats['avg_usage'] > 0 else 0
        )
    finally:
        cursor.close()
        conn.close()
