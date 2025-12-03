import asyncio
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User, Role, UserRole, Permission, RolePermission
from app.models.property import Property, Destination
from app.models.amenity import Amenity
from app.models.policy import Policy
from app.core.config import settings
from passlib.context import CryptContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Create Roles
        # roles = ["admin", "manager", "customer", "property_owner"]
        # role_map = {}
        # for role_name in roles:
        #     result = await session.execute(select(Role).where(Role.name == role_name))
        #     role = result.scalars().first()
        #     if not role:
        #         role = Role(name=role_name, description=f"{role_name} role")
        #         session.add(role)
        #         await session.commit()
        #         await session.refresh(role)
        #         logger.info(f"Created role: {role_name}")
        #     role_map[role_name] = role

        # 2. Create Permissions (Sample)
        permissions = [
            {"code": "user:read", "description": "Read users"},
            {"code": "user:write", "description": "Create/Update users"},
            {"code": "property:read", "description": "Read properties"},
            {"code": "property:write", "description": "Create/Update properties"},
            {"code": "booking:read", "description": "Read bookings"},
            {"code": "booking:write", "description": "Create/Update bookings"},
        ]
        
        for perm_data in permissions:
            result = await session.execute(select(Permission).where(Permission.code == perm_data["code"]))
            perm = result.scalars().first()
            if not perm:
                perm = Permission(**perm_data)
                session.add(perm)
                await session.commit()
                logger.info(f"Created permission: {perm_data['code']}")

        # # 3. Create Admin User
        # result = await session.execute(select(User).where(User.email == settings.FIRST_SUPERUSER))
        # user = result.scalars().first()
        # if not user:
        #     user = User(
        #         email=settings.FIRST_SUPERUSER,
        #         password_hash=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
        #         full_name="Super Admin",
        #         is_active=True
        #     )
        #     session.add(user)
        #     await session.commit()
        #     await session.refresh(user)
            
        #     # Assign Admin Role
        #     user_role = UserRole(user_id=user.id, role_id=role_map["admin"].id)
        #     session.add(user_role)
        #     await session.commit()
            
        #     logger.info(f"Created admin user: {settings.FIRST_SUPERUSER}")
        # else:
        #      # Ensure admin role exists
        #     result = await session.execute(select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role_map["admin"].id))
        #     if not result.scalars().first():
        #         user_role = UserRole(user_id=user.id, role_id=role_map["admin"].id)
        #         session.add(user_role)
        #         await session.commit()

        # 4. Create Master Amenities
        amenities = [
            {"code": "wifi", "name": "Wi-Fi", "category": "General", "description": "High-speed internet access"},
            {"code": "pool", "name": "Swimming Pool", "category": "Wellness", "description": "Outdoor swimming pool"},
            {"code": "ac", "name": "Air Conditioning", "category": "General", "description": "Climate control"},
            {"code": "parking", "name": "Parking", "category": "General", "description": "Free parking on premises"},
            {"code": "breakfast", "name": "Breakfast", "category": "Dining", "description": "Complimentary breakfast"},
            {"code": "gym", "name": "Gym", "category": "Wellness", "description": "Fitness center"},
        ]

        for am_data in amenities:
            result = await session.execute(select(Amenity).where(Amenity.code == am_data["code"]))
            amenity = result.scalars().first()
            if not amenity:
                amenity = Amenity(**am_data)
                session.add(amenity)
                await session.commit()
                logger.info(f"Created amenity: {am_data['name']}")

        # 5. Create Master Policies
        policies = [
            {"code": "cancellation_flexible", "title": "Flexible Cancellation", "category": "Cancellation", "description": "Free cancellation until 24 hours before check-in."},
            {"code": "cancellation_strict", "title": "Strict Cancellation", "category": "Cancellation", "description": "No refund if cancelled."},
            {"code": "check_in_out", "title": "Check-in / Check-out", "category": "House Rules", "description": "Check-in after 2PM, Check-out before 11AM."},
            {"code": "no_smoking", "title": "No Smoking", "category": "House Rules", "description": "Smoking is not allowed inside the property."},
            {"code": "pets_allowed", "title": "Pets Allowed", "category": "House Rules", "description": "Pets are allowed with prior notice."},
        ]

        for pol_data in policies:
            result = await session.execute(select(Policy).where(Policy.code == pol_data["code"]))
            policy = result.scalars().first()
            if not policy:
                policy = Policy(**pol_data)
                session.add(policy)
                await session.commit()
                logger.info(f"Created policy: {pol_data['title']}")

        # # 6. Create Sample Destinations
        # destinations = [
        #     {"name": "Bali", "slug": "bali", "description": "Island of Gods", "country": "Indonesia"},
        #     {"name": "Paris", "slug": "paris", "description": "City of Light", "country": "France"},
        #     {"name": "New York", "slug": "new-york", "description": "The Big Apple", "country": "USA"},
        #     {"name": "Tokyo", "slug": "tokyo", "description": "Neon City", "country": "Japan"},
        # ]
        
        # for dest_data in destinations:
        #     result = await session.execute(select(Destination).where(Destination.slug == dest_data["slug"]))
        #     dest = result.scalars().first()
        #     if not dest:
        #         dest = Destination(**dest_data)
        #         session.add(dest)
        #         await session.commit()
        #         logger.info(f"Created destination: {dest_data['name']}")

        # # 7. Create Sample Properties
        # # Need to fetch a destination first
        # result = await session.execute(select(Destination).where(Destination.slug == "bali"))
        # bali = result.scalars().first()
        
        # if bali:
        #     props = [
        #         {"name": "Bali Villa 1", "slug": "bali-villa-1", "overview": "Luxury Villa"},
        #         {"name": "Bali Villa 2", "slug": "bali-villa-2", "overview": "Beachfront Villa"},
        #         {"name": "Bali Villa 3", "slug": "bali-villa-3", "overview": "Jungle Villa"},
        #     ]
            
        #     for p_data in props:
        #         result = await session.execute(select(Property).where(Property.slug == p_data["slug"]))
        #         prop = result.scalars().first()
        #         if not prop:
        #             prop = Property(
        #                 name=p_data["name"],
        #                 slug=p_data["slug"],
        #                 overview=p_data["overview"],
        #                 destination_id=bali.id,
        #                 created_by=user.id if user else None
        #             )
        #             session.add(prop)
        #             await session.commit()
        #             logger.info(f"Created property: {p_data['name']}")

if __name__ == "__main__":
    asyncio.run(seed_data())
