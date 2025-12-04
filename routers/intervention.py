from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models import InterventionModel
from schemas import Intervention, InterventionCreate, InterventionUpdate

router = APIRouter(prefix="/interventions", tags=["Interventions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Intervention, status_code=status.HTTP_201_CREATED)
def create_intervention(intervention: InterventionCreate, db: Session = Depends(get_db)):
    db_intervention = InterventionModel(**intervention.dict())
    db.add(db_intervention)
    db.commit()
    db.refresh(db_intervention)
    return db_intervention

@router.get("/", response_model=List[Intervention])
def read_interventions(db: Session = Depends(get_db)):
    return db.query(InterventionModel).all()

@router.get("/{intervention_id}", response_model=Intervention)
def read_intervention(intervention_id: int, db: Session = Depends(get_db)):
    intervention = db.query(InterventionModel).filter(InterventionModel.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return intervention

@router.put("/{intervention_id}", response_model=Intervention)
def update_intervention(intervention_id: int, intervention_update: InterventionUpdate, db: Session = Depends(get_db)):
    intervention = db.query(InterventionModel).filter(InterventionModel.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    for key, value in intervention_update.dict().items():
        setattr(intervention, key, value)
    db.commit()
    db.refresh(intervention)
    return intervention

@router.delete("/{intervention_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_intervention(intervention_id: int, db: Session = Depends(get_db)):
    intervention = db.query(InterventionModel).filter(InterventionModel.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    db.delete(intervention)
    db.commit()
    return None
