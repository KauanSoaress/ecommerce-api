from fastapi import FastAPI
from src.api.v1.router import api_router
from contextlib import asynccontextmanager
from src.db.seed import initialize_system


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    await initialize_system()

    yield
    print("Stopping application...")

app = FastAPI(
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def main():
    return {"Status": "OK."}
