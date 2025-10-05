from fastapi import FastAPI
from api import location, fertilizer, water, yield_api, crop, livestock

app = FastAPI(title="KrishiPatha Backend", version="1.0")

# include routes
app.include_router(location.router, prefix="/analyze", tags=["Location"])
app.include_router(crop.router, prefix="/analyze", tags=["Crops"])
app.include_router(livestock.router, prefix="/analyze", tags=["Livestock"])
app.include_router(fertilizer.router, prefix="/analyze", tags=["Fertilizer"])
app.include_router(water.router, prefix="/analyze", tags=["Water"])
app.include_router(yield_api.router, prefix="/analyze", tags=["Yield"])

@app.get("/")
def root():
    return {"msg": "KrishiPatha Backend is running 🚜"}
