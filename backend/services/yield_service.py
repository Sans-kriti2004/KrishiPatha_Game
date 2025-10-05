def predict(env: dict):
    """
    Predict crop yield and NDVI score.
    Mock logic for now.
    """
    crop = env.get("crop", "Wheat")
    area = env.get("area", 1.0)  # hectares

    base_yield = 2000  # kg/ha
    factor = 1.2 if crop.lower() == "rice" else 0.9
    predicted_yield = base_yield * factor * area

    ndvi = 0.8  # mock vegetation index

    return predicted_yield, ndvi
