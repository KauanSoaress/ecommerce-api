from src.config import CONFIG
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DB_URL = f"postgresql+asyncpg://{CONFIG.DATABASE_USER}:{CONFIG.DATABASE_PASSWORD}@postgres:5432/{CONFIG.DATABASE_NAME}"

engine = create_async_engine(
    url=DB_URL,
    echo=True,
)

async def init_db():
    async with engine.begin() as conn:
        statement = text("""SELECT 'Database Initialized'""")
        result = await conn.execute(statement)
        print(result.all())