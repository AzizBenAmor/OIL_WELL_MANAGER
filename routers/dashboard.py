from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import WellModel,SiteModel,ProductionModel , IncidentModel , InterventionModel
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
from ml.predictions import predict_production, predict_incident_risk, get_recommendations
from datetime import datetime, timedelta
from sqlalchemy import func, desc

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_dashboard_data(db: Session):
    """Helper function to get dashboard data for HTML template"""
    # Get dashboard overview data
    overview = await get_dashboard_overview(db)
    
    # Format it for the template
    return {
        "summary": overview.get("summary", {}),
        "wells": overview.get("wells", []),
        "total_wells": overview.get("total_wells", 0),
        "active_wells": overview.get("active_wells", 0),
        "high_risk_count": overview.get("summary", {}).get("high_risk_wells", 0),
        "recent_incidents": overview.get("recent_incidents", 0)
    }
    
@router.get("/production/{well_id}")
def production_dashboard(request: Request, well_id: int, db: Session = Depends(get_db)):
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return templates.TemplateResponse(
        "production.html", 
        {"request": request, "well_id": well_id , "well_name": well.name}
    )
    
@router.get("/production/site/{site_id}")
def production_site_dashboard(request: Request, site_id: int, db: Session = Depends(get_db)):
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    
    return templates.TemplateResponse(
        "production_site.html",
        {
            "request": request,
            "site_id": site_id,
            "site_name": site.name
        }
    )

@router.get("/uptime/{well_id}")
def uptime_dashboard(request: Request, well_id: int, db: Session = Depends(get_db)):
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return templates.TemplateResponse(
        "uptime.html", 
        {"request": request, "well_id": well_id , "well_name": well.name}
    )


@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview with ML predictions"""
    
    # Get all wells with latest production
    wells = db.query(WellModel).all()
    
    dashboard_data = {
        "total_wells": len(wells),
        "active_wells": len([w for w in wells if w.status == "active"]),
        "total_sites": db.query(SiteModel).count(),
        "active_interventions": db.query(InterventionModel).filter(
            InterventionModel.end_time == None
        ).count(),
        "recent_incidents": db.query(IncidentModel).filter(
            IncidentModel.date >= datetime.now() - timedelta(days=7)
        ).count(),
        "wells": []
    }
    
    # Add ML predictions for each well
    for well in wells:
        # Get latest production data
        latest_production = db.query(ProductionModel).filter(
            ProductionModel.well_id == well.id
        ).order_by(desc(ProductionModel.timestamp)).first()
        
        # Get recent incidents count
        recent_incidents = db.query(IncidentModel).filter(
            IncidentModel.well_id == well.id,
            IncidentModel.date >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Prepare data for ML prediction
        well_data = {
            'flow_rate': latest_production.flow_rate if latest_production else 100.0,
            'pressure': latest_production.pressure if latest_production else 50.0,
            'temperature': latest_production.temperature if latest_production else 75.0,
            'depth': well.depth,
            'recent_incidents': recent_incidents,
            'status_code': 1 if well.status == "active" else 0,
            'month': datetime.now().month,
            'day_of_week': datetime.now().weekday()
        }
        
        # Get ML predictions
        predicted_production = predict_production(well_data)
        risk_prediction = predict_incident_risk(well_data)
        
        # Get recommendations
        current_production = latest_production.quantity_produced if latest_production else 0
        recommendations = get_recommendations(
            risk_prediction["level"],
            current_production,
            predicted_production
        )
        
        # Add well data to dashboard
        dashboard_data["wells"].append({
            "id": well.id,
            "name": well.name,
            "site": well.site.name if well.site else "Unknown",
            "status": well.status,
            "depth": well.depth,
            "current_production": current_production,
            "predicted_production": predicted_production,
            "incident_risk": risk_prediction,
            "recommendations": recommendations,
            "last_update": latest_production.timestamp if latest_production else None
        })
    
    # Calculate summary metrics
    if dashboard_data["wells"]:
        total_production = sum(w["current_production"] for w in dashboard_data["wells"])
        avg_production = total_production / len(dashboard_data["wells"])
        
        high_risk_wells = [w for w in dashboard_data["wells"] if w["incident_risk"]["level"] == "High"]
        
        dashboard_data["summary"] = {
            "average_production": avg_production,
            "total_daily_production": total_production,
            "high_risk_wells": len(high_risk_wells),
            "production_efficiency": (avg_production / 100) * 100  # Simplified metric
        }
    
    return dashboard_data

@router.get("/predict/{well_id}")
async def predict_for_well(well_id: int, db: Session = Depends(get_db)):
    """Get ML predictions for a specific well"""
    
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    
    # Get latest production data
    latest_production = db.query(ProductionModel).filter(
        ProductionModel.well_id == well_id
    ).order_by(desc(ProductionModel.timestamp)).first()
    
    # Get recent incidents
    recent_incidents = db.query(IncidentModel).filter(
        IncidentModel.well_id == well_id,
        IncidentModel.date >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Prepare data for ML
    well_data = {
        'flow_rate': latest_production.flow_rate if latest_production else 100.0,
        'pressure': latest_production.pressure if latest_production else 50.0,
        'temperature': latest_production.temperature if latest_production else 75.0,
        'depth': well.depth,
        'recent_incidents': recent_incidents,
        'status_code': 1 if well.status == "active" else 0,
        'month': datetime.now().month,
        'day_of_week': datetime.now().weekday()
    }
    
    # Get predictions
    predicted_production = predict_production(well_data)
    risk_prediction = predict_incident_risk(well_data)
    
    current_production = latest_production.quantity_produced if latest_production else 0
    recommendations = get_recommendations(
        risk_prediction["level"],
        current_production,
        predicted_production
    )
    
    return {
        "well": {
            "id": well.id,
            "name": well.name,
            "status": well.status
        },
        "current_production": current_production,
        "predicted_production": predicted_production,
        "production_change": ((predicted_production - current_production) / current_production * 100 
                            if current_production > 0 else 0),
        "incident_risk": risk_prediction,
        "recommendations": recommendations,
        "prediction_time": datetime.now()
    }

@router.post("/predict/custom")
async def custom_prediction(data: dict):
    """Make custom prediction with provided data"""
    
    # Get predictions
    predicted_production = predict_production(data)
    risk_prediction = predict_incident_risk(data)
    
    # Get recommendations
    current_production = data.get('quantity_produced', 0)
    recommendations = get_recommendations(
        risk_prediction["level"],
        current_production,
        predicted_production
    )
    
    return {
        "input_data": data,
        "predicted_production": predicted_production,
        "incident_risk": risk_prediction,
        "recommendations": recommendations,
        "prediction_time": datetime.now()
    }

@router.get("/ml/status")
async def get_ml_status():
    """Check if ML models are loaded"""
    from ml.predictions import MODELS_LOADED, features
    
    return {
        "models_loaded": MODELS_LOADED,
        "features_used": features,
        "models_available": ["production_predictor", "incident_risk_predictor"]
    }

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Serve the main dashboard HTML page"""
    
    # Get data for the dashboard
    dashboard_data = await get_dashboard_data(db)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "data": dashboard_data
        }
    )
