from fastapi import APIRouter, HTTPException
from api.schemas import PredictRequest, PredictResponse
from ml.predict import predict_usage_risk

router = APIRouter(tags=["Prediction"])

@router.post("/predict-usage-risk", response_model=PredictResponse)
def predict_risk(request: PredictRequest):
    features = {
        "avg_usage": request.avg_usage,
        "growth_rate": request.growth_rate,
        "variability": request.variability,
        "peak_ratio": 1.2
    }
    
    result = predict_usage_risk(features)
    
    if "error" in result:
        raise HTTPException(status_code=503, detail=result["error"])
        
    return PredictResponse(
        congestion_risk=result["congestion_risk"],
        anomaly_flag=result["anomaly_flag"],
        score=result["score"]
    )
