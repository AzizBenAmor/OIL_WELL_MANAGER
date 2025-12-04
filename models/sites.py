from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship


class SiteModel(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    description = Column(String)

    wells = relationship("WellModel", back_populates="site")
