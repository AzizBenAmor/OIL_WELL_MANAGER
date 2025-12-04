from pydantic import BaseModel
from typing import Optional

class SiteBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None

class SiteCreate(SiteBase):
    pass

class SiteUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    description: Optional[str]

class Site(SiteBase):
    id: int

    class Config:
        orm_mode = True
