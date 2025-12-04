from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal, OilWellModel, create_db_and_tables
from schemas import OilWell, OilWellCreate

app = FastAPI(title="Oil Well Management API")
create_db_and_tables()


# Dependency: Get the Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoints (CRUD) ---

@app.post("/wells/", response_model=OilWell, status_code=status.HTTP_201_CREATED)
def create_oil_well(well: OilWellCreate, db: Session = Depends(get_db)):
    """Creates a new oil well record."""
    db_well = OilWellModel(**well.dict())
    db.add(db_well)
    db.commit()
    db.refresh(db_well)
    return db_well


@app.get("/wells/", response_model=List[OilWell])
def read_oil_wells(db: Session = Depends(get_db)):
    """Retrieves a list of all oil wells."""
    wells = db.query(OilWellModel).all()
    return wells


@app.get("/wells/{well_id}", response_model=OilWell)
def read_oil_well(well_id: int, db: Session = Depends(get_db)):
    """Retrieves a single oil well by ID."""
    well = db.query(OilWellModel).filter(OilWellModel.id == well_id).first()
    if well is None:
        raise HTTPException(status_code=404, detail="Oil Well not found")
    return well


@app.put("/wells/{well_id}", response_model=OilWell)
def update_oil_well(well_id: int, well_update: OilWellCreate, db: Session = Depends(get_db)):
    """Updates an existing oil well record."""
    db_well = db.query(OilWellModel).filter(OilWellModel.id == well_id).first()

    if db_well is None:
        raise HTTPException(status_code=404, detail="Oil Well not found")

    for key, value in well_update.dict().items():
        setattr(db_well, key, value)

    db.commit()
    db.refresh(db_well)
    return db_well


@app.delete("/wells/{well_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_oil_well(well_id: int, db: Session = Depends(get_db)):
    """Deletes an oil well record by ID."""
    db_well = db.query(OilWellModel).filter(OilWellModel.id == well_id).first()

    if db_well is None:
        raise HTTPException(status_code=404, detail="Oil Well not found")

    db.delete(db_well)
    db.commit()
    return None