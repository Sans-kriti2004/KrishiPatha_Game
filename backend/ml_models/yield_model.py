# backend/ml_models/yield_model.py
import random

def predict_yield(params: dict) -> dict:
    """
    Placeholder for ML-based yield and sustainability model.
    Replace with real ML logic later.
    """
    yield_base = random.uniform(2000, 5000)
    score_base = random.uniform(60, 95)

    if params["irrigation"].lower() == "drip":
        yield_base *= 1.1
        score_base += 3
    elif params["irrigation"].lower() == "manual":
        yield_base *= 0.9
        score_base -= 5

    if params["water_amount"] == "Low":
        yield_base *= 0.8
    elif params["water_amount"] == "High":
        yield_base *= 1.05

    return {
        "yield_value": round(yield_base, 2),
        "score": round(min(max(score_base, 0), 100), 2),
    }
