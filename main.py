# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from geopy.geocoders import Nominatim
from datetime import datetime
import numpy as np

app = FastAPI(title="Agri Prediction API")

# -----------------------------
# 1️⃣ Load trained models
# -----------------------------
yield_model = joblib.load("models/yield_model.pkl")
ndvi_model = joblib.load("models/ndvi_model.pkl")
sustain_model = joblib.load("models/sustain_model.pkl")

# -----------------------------
# 2️⃣ Load your dataset for mapping nearest location
# -----------------------------
df = pd.read_csv("nasa_agriculture_master_updated.csv")

# -----------------------------
# 3️⃣ Define input schema
# -----------------------------
class InputData(BaseModel):
    date: str        # format: "dd/mm/yyyy"
    latitude: float = None
    longitude: float = None
    city: str = None

# -----------------------------
# 4️⃣ Helper function: convert city to lat/lon
# -----------------------------
def get_lat_lon_from_city(city_name):
    geolocator = Nominatim(user_agent="agri_prediction_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    return None, None

# -----------------------------
# 5️⃣ Helper function: map to nearest available field
# -----------------------------
def map_to_nearest_field(lat, lon, year):
    df_year = df[df['year'] == year]
    df_year['dist'] = np.sqrt((df_year['latitude'] - lat)**2 + (df_year['longitude'] - lon)**2)
    nearest = df_year.loc[df_year['dist'].idxmin()]
    return nearest

# -----------------------------
# 6️⃣ API endpoint
# -----------------------------
@app.post("/predict")
def predict(data: InputData):
    # Step 1: Get lat/lon from city if provided
    lat, lon = data.latitude, data.longitude
    if data.city and (lat is None or lon is None):
        lat, lon = get_lat_lon_from_city(data.city)
        if lat is None:
            return {"error": "City not found"}

    # Step 2: Extract year from date
    try:
        date_obj = datetime.strptime(data.date, "%d/%m/%Y")
        year = date_obj.year
    except:
        return {"error": "Date format should be dd/mm/yyyy"}

    # Step 3: Map to nearest available field data
    nearest_field = map_to_nearest_field(lat, lon, year)

    # Step 4: Prepare features for each model
    # NDVI features
    ndvi_features = nearest_field[[
        'latitude','longitude','year','season_number','season_length_days',
        'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index'
    ]].to_frame().T

    # Yield features
    yield_features = nearest_field[[
        'latitude','longitude','year','season_number','season_length_days',
        'ndvi_peak','ndvi_mean','ndvi_auc','ndvi_slope_mid',
        'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index'
    ]].to_frame().T

    # Sustainability features
    sustain_features = nearest_field[[
        'latitude','longitude','year','season_number','season_length_days',
        'ndvi_peak','ndvi_mean','ndvi_auc','ndvi_slope_mid',
        'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index','yield_kg_ha'
    ]].to_frame().T

    # Step 5: Make predictions
    ndvi_pred = ndvi_model.predict(ndvi_features)[0]
    yield_pred = yield_model.predict(yield_features)[0]
    sustain_pred = sustain_model.predict(sustain_features)[0]

    # Step 6: Return JSON response
    return {
        "latitude": lat,
        "longitude": lon,
        "year": year,
        "ndvi_prediction": ndvi_pred,
        "yield_prediction": yield_pred,
        "sustainability_score": sustain_pred
    }
