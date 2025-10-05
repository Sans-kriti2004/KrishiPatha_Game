from fastapi import APIRouter
from pydantic import BaseModel
from services import crop_service, livestock_service, fertilizer_service, water_service, yield_service

router = APIRouter()

class LocationInput(BaseModel):
    lat: float
    lon: float

@router.post("/location")
def analyze_location(data: LocationInput):
    # mock env data (replace later with real ML)
    env = {"soil": "loamy", "rainfall": 700, "temperature": 25}
    
    crops = crop_service.recommend(env)
    livestock = livestock_service.recommend(env)
    fertilizer = fertilizer_service.recommend(env, ph=6.5)
    water = water_service.predict(env)
    yield_pred, ndvi = yield_service.predict(env)
    
    return {
        "location": {"lat": data.lat, "lon": data.lon},
        "environment": env,
        "recommendations": {
            "crops": crops,
            "livestock": livestock,
            "fertilizer": fertilizer,
            "water": water,
            "yield_prediction": yield_pred,
            "ndvi_score": ndvi
        }
    }
