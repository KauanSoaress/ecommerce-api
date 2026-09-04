import asyncio
from sqlalchemy import select
from src.config import CONFIG
from src.db.models.users import User
from src.db.connection import async_session
from src.core.security import hash_password


async def initialize_system():
    await create_admin()


async def create_admin():
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == CONFIG.FIRST_ADMIN_EMAIL)
        )

        if result.scalar_one_or_none():
            print("Admin already exists.")
            return

        admin = User(
            username="admin",
            email=CONFIG.FIRST_ADMIN_EMAIL,
            hashed_password=hash_password(CONFIG.FIRST_ADMIN_PASSWORD),
            is_admin=True,
        )

        session.add(admin)
        await session.commit()

        print("Admin created.")

if __name__ == "__main__":
    asyncio.run(create_admin())