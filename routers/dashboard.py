from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from models import WellModel,SiteModel
router = APIRouter(prefix="/dashboard", tags=["dashboard"])

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
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
    