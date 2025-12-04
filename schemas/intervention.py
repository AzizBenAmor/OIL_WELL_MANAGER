from pydantic import BaseModel
from datetime import datetime


class InterventionBase(BaseModel):
    well_id: int
    team_id: int
    start_time: datetime
    end_time: datetime | None = None
    operation: str
    notes: str | None = None


class InterventionCreate(InterventionBase):
    pass

class InterventionUpdate(InterventionBase):
    pass

class Intervention(InterventionBase):
    id: int

    class Config:
        from_attributes = True
