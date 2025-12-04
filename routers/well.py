from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models import WellModel
from schemas import Well, WellCreate, WellUpdate

router = APIRouter(prefix="/wells", tags=["Wells"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Well, status_code=status.HTTP_201_CREATED)
def create_well(well: WellCreate, db: Session = Depends(get_db)):
    db_well = WellModel(**well.dict())
    db.add(db_well)
    db.commit()
    db.refresh(db_well)
    return db_well

@router.get("/", response_model=List[Well])
def read_wells(db: Session = Depends(get_db)):
    return db.query(WellModel).all()

@router.get("/{well_id}", response_model=Well)
def read_well(well_id: int, db: Session = Depends(get_db)):
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    return well

@router.put("/{well_id}", response_model=Well)
def update_well(well_id: int, well_update: WellUpdate, db: Session = Depends(get_db)):
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    for key, value in well_update.dict().items():
        setattr(well, key, value)
    db.commit()
    db.refresh(well)
    return well

@router.delete("/{well_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_well(well_id: int, db: Session = Depends(get_db)):
    well = db.query(WellModel).filter(WellModel.id == well_id).first()
    if not well:
        raise HTTPException(status_code=404, detail="Well not found")
    db.delete(well)
    db.commit()
    return None
