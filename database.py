from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./oil_wells.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model (Table Definition) ---

class OilWellModel(Base):
    __tablename__ = "oil_wells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    production_rate = Column(Float)
    status = Column(String)

# Function to create all defined tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)