from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class WaterInput(BaseModel):
    crop: str
    rainfall: float

@router.post("/water")
def predict_water(data: WaterInput):
    # mock prediction
    water_need = "medium"
    if data.crop.lower() == "rice":
        water_need = "high"
    elif data.crop.lower() == "millet":
        water_need = "low"
    return {
        "crop": data.crop,
        "rainfall": data.rainfall,
        "predicted_water_need": water_need
    }
