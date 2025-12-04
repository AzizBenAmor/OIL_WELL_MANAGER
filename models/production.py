from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class ProductionModel(Base):
    __tablename__ = "production"

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"))
    timestamp = Column(String)
    flow_rate = Column(Float)
    pressure = Column(Float)
    temperature = Column(Float)
    quantity_produced = Column(Float)

    well = relationship("WellModel", back_populates="production_records")
