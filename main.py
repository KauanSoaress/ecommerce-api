from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    yield
    print("Stopping application...")

app = FastAPI(
    lifespan=lifespan,
)

@app.get("/")
def main():
    return {"Status": "OK."}
