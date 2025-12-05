from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from database import SessionLocal
from models import TeamModel ,InterventionModel
from schemas import Team, TeamCreate, TeamUpdate

router = APIRouter(prefix="/teams", tags=["Teams"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = TeamModel(**team.dict())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team

@router.get("/", response_model=List[Team])
def read_teams(db: Session = Depends(get_db)):
    return db.query(TeamModel).all()

@router.get("/{team_id}", response_model=Team)
def read_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.put("/{team_id}", response_model=Team)
def update_team(team_id: int, team_update: TeamUpdate, db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    for key, value in team_update.dict().items():
        setattr(team, key, value)
    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(TeamModel).filter(TeamModel.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(team)
    db.commit()
    return None

@router.get("/teams/productivity/{team_id}")
def get_team_productivity(team_id: int, db: Session = Depends(get_db)):
    try:
        # Query: Count interventions grouped by year
        results = (
            db.query(
                func.strftime('%Y', InterventionModel.start_time).label("year"),
                func.count(InterventionModel.id).label("intervention_count")
            )
            .filter(InterventionModel.team_id == team_id)
            .group_by("year")
            .order_by("year")
            .all()
        )

        # Convert query result → dict
        productivity = {
            row.year: row.intervention_count
            for row in results
        }

        return {"team_id": team_id, "productivity_per_year": productivity}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating productivity: {str(e)}"
        )
