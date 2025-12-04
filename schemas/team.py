from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    supervisor: str
  

class TeamCreate(TeamBase):
    pass

class TeamUpdate(TeamBase):
    pass

class Team(TeamBase):
    id: int

    class Config:
        from_attributes = True
