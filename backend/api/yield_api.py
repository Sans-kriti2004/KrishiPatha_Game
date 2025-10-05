from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class YieldInput(BaseModel):
    area: float
    crop: str

@router.post("/yield")
def predict_yield(data: YieldInput):
    # mock response for now
    return {
        "crop": data.crop,
        "area": data.area,
        "predicted_yield": 2500,  # placeholder
        "ndvi_score": 0.82
    }
