from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LivestockInput(BaseModel):
    temperature: float

@router.post("/livestock")
def recommend_livestock(data: LivestockInput):
    # mock livestock for now
    return {
        "input": data.model_dump(),
        "recommendations": ["Goat", "Cow"]
    }
