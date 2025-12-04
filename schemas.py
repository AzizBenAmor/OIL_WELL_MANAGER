from pydantic import BaseModel

# Schema for creating a new well (input)
class OilWellCreate(BaseModel):
    name: str
    location: str
    production_rate: float
    status: str

# Schema for reading a well (output, includes the ID)
class OilWell(OilWellCreate):
    id: int

    class Config:
        from_attributes = True