import asyncio
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, Role, UserRole
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERS = [
    {"email": "admin@bro.com", "password": "password", "role": "SYSTEM_ADMIN", "name": "System Admin"},
    {"email": "propadmin@bro.com", "password": "password", "role": "PROPERTY_ADMIN", "name": "Property Admin"},
    {"email": "propuser@bro.com", "password": "password", "role": "PROPERTY_USER", "name": "Property User"},
    {"email": "webadmin@bro.com", "password": "password", "role": "WEBSITE_ADMIN", "name": "Website Admin"},
    {"email": "webuser@bro.com", "password": "password", "role": "WEBSITE_USER", "name": "Website User"},
]

async def seed_users():
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Seeding Users...")
            for user_data in USERS:
                # Check if user exists
                result = await db.execute(select(User).where(User.email == user_data["email"]))
                existing_user = result.scalars().first()
                
                if not existing_user:
                    new_user = User(
                        email=user_data["email"],
                        password_hash=get_password_hash(user_data["password"]),
                        full_name=user_data["name"],
                        is_active=True
                    )
                    db.add(new_user)
                    await db.flush()
                    existing_user = new_user
                    logger.info(f"Created user: {user_data['email']}")
                else:
                    logger.info(f"User already exists: {user_data['email']}")
                
                # Assign Role
                result = await db.execute(select(Role).where(Role.name == user_data["role"]))
                role = result.scalars().first()
                
                if role:
                    # Check if assignment exists
                    result = await db.execute(
                        select(UserRole).where(
                            UserRole.user_id == existing_user.id,
                            UserRole.role_id == role.id
                        )
                    )
                    existing_assignment = result.scalars().first()
                    
                    if not existing_assignment:
                        new_assignment = UserRole(user_id=existing_user.id, role_id=role.id)
                        db.add(new_assignment)
                        logger.info(f"Assigned {user_data['role']} to {user_data['email']}")
                else:
                    logger.error(f"Role not found: {user_data['role']}")
            
            await db.commit()
            logger.info("User seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Error seeding users: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_users())
