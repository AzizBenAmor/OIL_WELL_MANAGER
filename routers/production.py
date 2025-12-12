from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
from sqlalchemy import func
from database import SessionLocal
from models import ProductionModel
from schemas import Production, ProductionCreate, ProductionUpdate , ProductionYearly

router = APIRouter(prefix="/production", tags=["Production"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Production, status_code=status.HTTP_201_CREATED)
def create_production(production: ProductionCreate, db: Session = Depends(get_db)):
    db_production = ProductionModel(**production.dict())
    db.add(db_production)
    db.commit()
    db.refresh(db_production)
    return db_production

@router.get('/well/{well_id}', response_model=List[ProductionYearly],status_code=status.HTTP_200_OK)
def get_production_by_well(well_id: int, db: Session = Depends(get_db)):
    try:
        productions = (
            db.query(
                func.substr(ProductionModel.timestamp, 1, 4).label("year"),
                func.sum(ProductionModel.quantity_produced).label("total_production")
            )
            .filter(ProductionModel.well_id == well_id)
            .group_by("year")
            .order_by("year")
            .all()
        )
        return [
            {"year": year, "total_production": total}
            for year, total in productions
        ]
    except  Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching production data: {str(e)}"
        )
@router.get("/", response_model=List[Production])
def read_productions(db: Session = Depends(get_db)):
    return db.query(ProductionModel).all()

@router.get("/{production_id}", response_model=Production)
def read_production(production_id: int, db: Session = Depends(get_db)):
    production = db.query(ProductionModel).filter(ProductionModel.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production record not found")
    return production

@router.put("/{production_id}", response_model=Production)
def update_production(production_id: int, production_update: ProductionUpdate, db: Session = Depends(get_db)):
    production = db.query(ProductionModel).filter(ProductionModel.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production record not found")
    for key, value in production_update.dict().items():
        setattr(production, key, value)
    db.commit()
    db.refresh(production)
    return production

@router.delete("/{production_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production(production_id: int, db: Session = Depends(get_db)):
    production = db.query(ProductionModel).filter(ProductionModel.id == production_id).first()
    if not production:
        raise HTTPException(status_code=404, detail="Production record not found")
    db.delete(production)
    db.commit()
    return None
