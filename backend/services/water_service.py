def predict(env: dict):
    """
    Predict water requirement for crops.
    Mock logic for now.
    """
    crop = env.get("crop", "Wheat")
    rainfall = env.get("rainfall", 600)

    if crop.lower() == "rice":
        need = "high"
    elif crop.lower() == "millet":
        need = "low"
    else:
        need = "medium"

    return {"crop": crop, "rainfall": rainfall, "water_need": need}
