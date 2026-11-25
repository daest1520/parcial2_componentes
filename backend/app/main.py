from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import initialize_database
from app.routers import trips, places, categories


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="API Planificador de viajes",
    version="2.0.0",
    description="API REST para gestionar viajes y lugares por visitar. Almacenamiento local SQLite.",
    lifespan=lifespan,
)


@app.get("/api/health", tags=["Estado"], summary="Verificar el estado de la API")
def health():
    return {
        "status": "ok",
        "service": "api-planificador-viajes",
        "database": "SQLite",
    }


app.include_router(trips.router)
app.include_router(places.router)
app.include_router(categories.router)
