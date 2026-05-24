from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from db.database import engine, Base
from models.schemas import Watercheck, Mediciones, EstandaresTDS
from routers import endpoints
from routers.startup import startup_database

@asynccontextmanager
async def lifespan( app : FastAPI ):
    await startup_database()
    yield

#########################################

Base.metadata.create_all( bind = engine )

app = FastAPI( lifespan=lifespan )

app.include_router( endpoints.router )

# Sirve el frontend desde /static
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(endpoints.router)

# Ruta raíz → entrega index.html
@app.get("/")
async def root():
    return FileResponse("static/index.html")
