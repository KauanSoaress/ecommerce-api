from sqlalchemy import text
from src.config import CONFIG
from sqlalchemy.ext.asyncio import create_async_engine
from src.db.models import Base, User

DB_URL = f"postgresql+asyncpg://{CONFIG.DATABASE_USER}:{CONFIG.DATABASE_PASSWORD}@postgres:5432/{CONFIG.DATABASE_NAME}"

engine = create_async_engine(
    url=DB_URL,
    echo=True,
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database initialized successfully.")