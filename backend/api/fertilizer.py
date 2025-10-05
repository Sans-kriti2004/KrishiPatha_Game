from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FertilizerInput(BaseModel):
    ph: float

@router.post("/fertilizer")
def recommend_fertilizer(data: FertilizerInput):
    # mock fertilizer recommendation
    if data.ph < 6.5:
        rec = "Add lime to increase soil pH"
    else:
        rec = "Use nitrogen-rich fertilizer"
    return {
        "ph": data.ph,
        "recommendation": rec
    }
