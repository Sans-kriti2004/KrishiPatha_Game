from fastapi import APIRouter
from pydantic import BaseModel
from ml_models.environment_model import get_environment_prediction

router = APIRouter()

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

class EnvironmentResponse(BaseModel):
    soil: str
    avg_rainfall: float
    avg_temp: float
    water_source: str
    recommended_crops: list[str]
    recommended_livestock: list[str]

@router.post("/environment", response_model=EnvironmentResponse)
async def analyze_environment(req: LocationRequest):
    """
    Endpoint: /analyze/environment
    Fetches real or simulated environment analysis from ML model
    """
    data = get_environment_prediction(req.latitude, req.longitude)
    return EnvironmentResponse(**data)
