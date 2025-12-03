import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.core.config import settings

async def reset_password():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER))
        user = result.scalars().first()
        
        if user:
            new_password = settings.FIRST_SUPERUSER_PASSWORD
            print(f"Resetting password for {user.email} to '{new_password}'")
            new_hash = get_password_hash(new_password)
            print(f"New Hash: {new_hash}")
            
            user.password_hash = new_hash
            session.add(user)
            await session.commit()
            print("Password reset successful.")
        else:
            print("Admin user not found.")

if __name__ == "__main__":
    asyncio.run(reset_password())
