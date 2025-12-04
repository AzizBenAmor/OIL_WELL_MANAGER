from pydantic import BaseModel
from typing import Optional

class ProductionBase(BaseModel):
    well_id: int
    timestamp: str
    flow_rate: Optional[float]
    pressure: Optional[float]
    temperature: Optional[float]
    quantity_produced: Optional[float]

class ProductionCreate(ProductionBase):
    pass

class ProductionUpdate(ProductionBase):
    pass

class Production(ProductionBase):
    id: int

    class Config:
        orm_mode = True
