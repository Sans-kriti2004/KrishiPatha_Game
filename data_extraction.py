import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# load your full dataset
df = pd.read_csv('global_large_12year_yield_dataset.csv')

# ---- 1️⃣ Yield Prediction Dataset ----
yield_cols = [
    'field_id','latitude','longitude','year','season_number','season_length_days',
    'ndvi_peak','ndvi_mean','ndvi_auc','ndvi_slope_mid',
    'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index',
    'yield_kg_ha'
]
df_yield = df[yield_cols].dropna(subset=['yield_kg_ha'])
df_yield.to_csv('data/yield_prediction.csv', index=False)

# ---- 2️⃣ NDVI Prediction Dataset ----
ndvi_cols = [
    'field_id','latitude','longitude','year','season_number','season_length_days',
    'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index','ndvi_peak'
]
df_ndvi = df[ndvi_cols].dropna(subset=['ndvi_peak'])
df_ndvi.to_csv('data/ndvi_prediction.csv', index=False)

# ---- 3️⃣ Sustainability Score Dataset ----
scaler = MinMaxScaler()
df_scaled = df[['yield_kg_ha','ndvi_mean','water_stress_index']].copy().dropna()
df_scaled[['yield_norm','ndvi_norm','stress_norm']] = scaler.fit_transform(df_scaled)
df['sustainability_score'] = (
    0.4 * df_scaled['yield_norm'] +
    0.3 * df_scaled['ndvi_norm'] +
    0.3 * (1 - df_scaled['stress_norm'])
)

sustain_cols = [
    'field_id','latitude','longitude','year','season_number','season_length_days',
    'ndvi_peak','ndvi_mean','ndvi_auc','ndvi_slope_mid',
    'precip_cum','rh_mean','gdd_cum','solar_cum','water_stress_index',
    'yield_kg_ha','sustainability_score'
]
df_sustain = df[sustain_cols].dropna(subset=['sustainability_score'])
df_sustain.to_csv('data/sustainability_score.csv', index=False)

print("✅ Created 3 training CSVs:")
print(" - data/yield_prediction.csv")
print(" - data/ndvi_prediction.csv")
print(" - data/sustainability_score.csv")
