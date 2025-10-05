from fastapi import APIRouter
from pydantic import BaseModel
from ml_models.yield_model import predict_yield

router = APIRouter()

class SimulationRequest(BaseModel):
    crop: str
    livestock: str
    water_amount: str
    irrigation: str
    soil: str
    temp: float
    rainfall: float

class SimulationResponse(BaseModel):
    yield_value: float
    score: float

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_farm(req: SimulationRequest):
    """
    Simulates yield prediction via ML model
    """
    result = predict_yield(req.dict())
    return SimulationResponse(**result)
