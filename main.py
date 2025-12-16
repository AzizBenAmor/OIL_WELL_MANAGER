from fastapi import FastAPI
from database import create_db_and_tables

from routers import (
    site,
    well,
    team,
    intervention,
    production,
    incident,
    dashboard
)
from ml.training import train_models  # Add this import
import joblib
import os

app = FastAPI(title="Oil Field Management")

# Create all DB tables
create_db_and_tables()
# Train ML models if they don't exist
if not os.path.exists('ml/models/production_model.pkl'):
    print("🔧 Initializing ML models...")
    try:
        train_models()
        print("✅ ML models trained successfully!")
    except Exception as e:
        print(f"⚠️  Could not train ML models: {e}")

app.include_router(dashboard.router)

# Register routers
app.include_router(site)
app.include_router(well)
app.include_router(team)
app.include_router(intervention)
app.include_router(production)
app.include_router(incident)

@app.get("/")
async def root():
    return {
        "message": "Oil Field Management API",
        "ml_integration": True,
        "endpoints": {
            "dashboard": "/dashboard/overview",
            "predict_for_well": "/dashboard/predict/{well_id}",
            "custom_prediction": "/dashboard/predict/custom",
            "ml_status": "/dashboard/ml/status"
        }
    }