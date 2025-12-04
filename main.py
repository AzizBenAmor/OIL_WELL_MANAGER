from fastapi import FastAPI
from database import create_db_and_tables

from routers import (
    site,
    well,
    team,
    intervention,
    production,
    incident,
)

app = FastAPI(title="Oil Field Management")

# Create all DB tables
create_db_and_tables()

# Register routers
app.include_router(site)
app.include_router(well)
app.include_router(team)
app.include_router(intervention)
app.include_router(production)
app.include_router(incident)
