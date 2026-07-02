from fastapi import FastAPI
from src.db.connection import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    await init_db()
    yield

    print("Shutting down application...")

app = FastAPI(
    lifespan=lifespan,
)

@app.get("/")
def main():
    return {"Status": "OK."}
