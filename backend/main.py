from fastapi import FastAPI
from api import location, yield_api

app = FastAPI(title="KrishiPatha Backend", version="1.0")

# ✅ include routers
app.include_router(location.router, prefix="/analyze", tags=["Location"])
app.include_router(yield_api.router, prefix="/analyze", tags=["Yield Simulation"])

@app.get("/")
def root():
    return {"msg": "KrishiPatha Backend is running 🌾"}
