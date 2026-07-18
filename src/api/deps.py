# src/api/deps.py
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import async_session  # ajuste o nome conforme seu connection.py


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_current_user():
    # Aqui você implementaria a lógica para obter o usuário atual
    # Por exemplo, você poderia verificar um token JWT ou uma sessão
    pass