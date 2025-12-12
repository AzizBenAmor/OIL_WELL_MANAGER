from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from database import SessionLocal
from models import SiteModel , WellModel , ProductionModel
from schemas import Site, SiteCreate, SiteUpdate

router = APIRouter(prefix="/sites", tags=["Sites"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Site, status_code=status.HTTP_201_CREATED)
def create_site(site: SiteCreate, db: Session = Depends(get_db)):
    db_site = SiteModel(**site.dict())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site

@router.get("/", response_model=List[Site])
def read_sites(db: Session = Depends(get_db)):
    return db.query(SiteModel).all()

@router.get("/{site_id}", response_model=Site)
def read_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.put("/{site_id}", response_model=Site)
def update_site(site_id: int, site_update: SiteUpdate, db: Session = Depends(get_db)):
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    for key, value in site_update.dict().items():
        setattr(site, key, value)
    db.commit()
    db.refresh(site)
    return site

@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: int, db: Session = Depends(get_db)):
    site = db.query(SiteModel).filter(SiteModel.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
    return None

@router.get("/{site_id}/wells")
def get_wells_by_site(site_id: int, db: Session = Depends(get_db)):
    wells = db.query(WellModel).filter(WellModel.site_id == site_id).all()
    return [{"id": well.id, "name": well.name} for well in wells]

@router.get("/{site_id}/production")
def get_production_by_site(site_id: int, db: Session = Depends(get_db)):
    # join WellModel and ProductionModel to filter by site_id
    productions = (
        db.query(
            ProductionModel.well_id,
            func.substr(ProductionModel.timestamp, 1, 4).label("year"),
            func.sum(ProductionModel.quantity_produced).label("total_production"),
        )
        .join(WellModel, ProductionModel.well_id == WellModel.id)
        .filter(WellModel.site_id == site_id)
        .group_by(ProductionModel.well_id, "year")
        .order_by(ProductionModel.well_id, "year")
        .all()
    )

    # Format the data grouped by well_id
    result = {}
    for well_id, year, total in productions:
        if well_id not in result:
            result[well_id] = []
        result[well_id].append({"year": year, "total_production": total})

    return result