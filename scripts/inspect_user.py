import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def check_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        for user in users:
            print(f"User: {user.email}")
            print(f"Hash: {user.password_hash}")
            print(f"Hash Length: {len(user.password_hash) if user.password_hash else 0}")

if __name__ == "__main__":
    asyncio.run(check_user())
