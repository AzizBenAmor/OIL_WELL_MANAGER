from pydantic import BaseModel


class WellBase(BaseModel):
    site_id: int
    name: str
    depth: float
    status: str


class WellCreate(WellBase):
    pass

class WellUpdate(WellBase):
    pass


class Well(WellBase):
    id: int

    class Config:
        from_attributes = True
