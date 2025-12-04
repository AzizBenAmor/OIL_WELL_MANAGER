from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"))
    incident_type = Column(String)
    severity = Column(String)
    date = Column(String)
    description = Column(String)
    resolved = Column(Integer, default=0)

    well = relationship("WellModel", back_populates="incidents")
