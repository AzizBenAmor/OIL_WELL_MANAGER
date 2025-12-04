from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class WellModel(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), index=True)
    name = Column(String, index=True)
    depth = Column(Float)
    status = Column(String)

    site = relationship("SiteModel", back_populates="wells")
    interventions = relationship("InterventionModel", back_populates="well")
    production_records = relationship("ProductionModel", back_populates="well", cascade="all, delete")
    incidents = relationship("IncidentModel", back_populates="well", cascade="all, delete")
