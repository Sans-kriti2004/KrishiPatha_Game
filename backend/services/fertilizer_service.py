def recommend(env: dict, ph: float):
    """
    Recommend fertilizer based on soil pH.
    Mock logic for now.
    """
    if ph < 6.0:
        rec = "Add lime to increase soil pH"
    elif ph > 7.5:
        rec = "Add sulfur to lower soil pH"
    else:
        rec = "Use nitrogen-rich fertilizer"

    return {"ph": ph, "fertilizer": rec}
