from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class InterventionModel(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    operation = Column(String)
    notes = Column(String)

    well = relationship("WellModel", back_populates="interventions")
    team = relationship("TeamModel", back_populates="interventions")
