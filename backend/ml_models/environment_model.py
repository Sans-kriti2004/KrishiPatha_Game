# backend/ml_models/environment_model.py
import random

def get_environment_prediction(lat: float, lon: float) -> dict:
    """
    Placeholder for ML-based environment prediction.
    Replace this with actual ML inference or pipeline call.
    """

    # Mock-up logic for now (randomized results)
    soils = ["sandy", "loamy", "clay"]
    soil = random.choice(soils)
    avg_temp = round(random.uniform(20, 35), 1)
    avg_rainfall = round(random.uniform(400, 900), 1)
    water_source = random.choice(["river", "tube well", "rain-fed"])

    if soil == "clay":
        crops = ["Rice", "Wheat", "Sugarcane"]
    elif soil == "sandy":
        crops = ["Millet", "Maize", "Groundnut"]
    else:
        crops = ["Wheat", "Maize", "Pulses"]

    livestock = ["Goat", "Cow", "Chicken"]

    return {
        "soil": soil,
        "avg_temp": avg_temp,
        "avg_rainfall": avg_rainfall,
        "water_source": water_source,
        "recommended_crops": crops,
        "recommended_livestock": livestock,
    }
