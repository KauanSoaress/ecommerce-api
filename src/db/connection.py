from src.config import CONFIG
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DB_URL = f"postgresql+asyncpg://{CONFIG.DATABASE_USER}:{CONFIG.DATABASE_PASSWORD}@postgres:5432/{CONFIG.DATABASE_NAME}"

engine = create_async_engine(
    url=DB_URL,
    echo=True,
)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
