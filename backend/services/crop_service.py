def recommend(env: dict):
    """
    Recommend crops based on environment.
    Currently returns mock data — replace with ML model later.
    """
    soil = env.get("soil", "loamy")
    temp = env.get("temperature", 25)

    if soil == "clay":
        recs = ["Rice", "Wheat"]
    elif soil == "sandy":
        recs = ["Millet", "Maize"]
    else:
        recs = ["Wheat", "Maize"]

    return {"soil": soil, "temperature": temp, "crops": recs}
