from pydantic import BaseModel
from typing import List

class UsageSummary(BaseModel):
    total_calls: int
    total_sms: int
    total_internet_mb: float
    peak_hour: int
    busiest_region: str

class HourlyUsage(BaseModel):
    hour: int
    calls: int
    sms: int
    internet_mb: float

class RegionUsage(BaseModel):
    region: str
    hourly_distribution: List[HourlyUsage]
    trend: List[float]

class PeakHour(BaseModel):
    hour: int
    total_usage: float

class PeakRegion(BaseModel):
    region: str
    total_usage: float

class PeakTraffic(BaseModel):
    top_hours: List[PeakHour]
    top_regions: List[PeakRegion]

class MLFeatures(BaseModel):
    region: str
    avg_usage: float
    growth_rate: float
    variability: float
    peak_ratio: float

class PredictRequest(BaseModel):
    region: str
    avg_usage: float
    growth_rate: float
    variability: float

class PredictResponse(BaseModel):
    congestion_risk: str
    anomaly_flag: bool
    score: float
