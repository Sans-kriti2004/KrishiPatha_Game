from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CropInput(BaseModel):
    soil: str
    rainfall: float
    temperature: float

@router.post("/crops")
def recommend_crops(data: CropInput):
    # mock crops for now
    return {
        "input": data.model_dump(),
        "recommendations": ["Wheat", "Rice", "Maize"]
    }
