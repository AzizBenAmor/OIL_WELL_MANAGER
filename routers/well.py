from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sqlalchemy import func, extract
from database import SessionLocal
from models import WellModel ,IncidentModel,  InterventionModel
from schemas import Well, WellCreate, WellUpdate
from typing import Any

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
@router.get("/uptime/{well_id}", response_model=Any,status_code=status.HTTP_200_OK)
def get_yearly_uptime_percentages(well_id: int,db: Session = Depends(get_db)):
    try:
        results = {}

        # First, get the distinct years for incidents and interventions for this well
        incident_years = db.query(
            func.strftime('%Y', IncidentModel.date).label('year')
        ).filter(IncidentModel.well_id == well_id).distinct().all()

        intervention_years = db.query(
            extract('year', InterventionModel.start_time).label('year')
        ).filter(InterventionModel.well_id == well_id).distinct().all()
        
        years = set()

        # Convert incident years from strings to int
        incident_years_int = {int(y[0]) for y in incident_years if y[0] is not None}

        # intervention years are likely already int, but let's be sure by converting too
        intervention_years_int = {int(y[0]) for y in intervention_years if y[0] is not None}

        years = incident_years_int | intervention_years_int

        for year in sorted(years):
            # Define the time window for the year
            start_period = datetime(year, 1, 1)
            end_period = datetime(year, 12, 31, 23, 59, 59)
            total_seconds = 365 * 24 * 3600  # seconds in a non-leap year

            # Calculate intervention downtime in this year
            interventions = db.query(InterventionModel).filter(
                InterventionModel.well_id == well_id,
                InterventionModel.end_time >= start_period,
                InterventionModel.start_time <= end_period
            ).all()

            intervention_downtime = 0
            for intervention in interventions:
                # Clamp times to year boundaries
                start = max(intervention.start_time, start_period)
                end = min(intervention.end_time, end_period)
                intervention_downtime += (end - start).total_seconds()

            # Calculate incident downtime (1 day per incident in this year)
            incidents_count = db.query(IncidentModel).filter(
                IncidentModel.well_id == well_id,
                IncidentModel.date >= start_period.strftime('%Y-%m-%d'),
                IncidentModel.date <= end_period.strftime('%Y-%m-%d')
            ).count()

            incident_downtime = incidents_count * 24 * 3600  # 1 day in seconds per incident

            total_downtime = intervention_downtime + incident_downtime
            uptime_seconds = max(0, total_seconds - total_downtime)

            uptime_percentage = (uptime_seconds / total_seconds) * 100 if total_seconds > 0 else 0
            results[year] = str(round(uptime_percentage, 2)) + "%"

        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while calculating uptime percentages: {str(e)}"
        )