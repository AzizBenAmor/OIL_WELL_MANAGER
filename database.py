from sqlalchemy import create_engine # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import sessionmaker, declarative_base # pyright: ignore[reportMissingImports]

# --- DB CONFIG ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./oil_wells.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


from models import (
    SiteModel, WellModel, TeamModel, InterventionModel, ProductionModel, IncidentModel
)

def create_db_and_tables():
    # Just call create_all on Base, no need to explicitly import the models again here.
    Base.metadata.create_all(bind=engine)

