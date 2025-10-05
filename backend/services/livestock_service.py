def recommend(env: dict):
    """
    Recommend livestock based on climate.
    Mock logic for now.
    """
    temp = env.get("temperature", 25)

    if temp > 30:
        recs = ["Goat", "Chicken"]
    else:
        recs = ["Cow", "Goat"]

    return {"temperature": temp, "livestock": recs}
