from fastapi import FastAPI
from app.database import database
from app.routes import auth, chart

from app.database import metadata, engine

app = FastAPI()

# Include routes
app.include_router(auth.router)
app.include_router(chart.router)

# Create tables
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
