from pydantic import BaseModel
from typing import Optional

class IncidentBase(BaseModel):
    well_id: int
    incident_type: str
    severity: str
    date: str
    description: Optional[str] = None
    resolved: Optional[int] = 0

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(IncidentBase):
    pass

class Incident(IncidentBase):
    id: int

    class Config:
        orm_mode = True
