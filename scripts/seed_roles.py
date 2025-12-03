import asyncio
import logging
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import Role, Permission, RolePermission

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define Permissions
PERMISSIONS = [
    # Property Permissions
    {"code": "PROPERTY_READ", "description": "View property details"},
    {"code": "PROPERTY_CREATE", "description": "Create new properties"},
    {"code": "PROPERTY_UPDATE", "description": "Update property details"},
    {"code": "PROPERTY_DELETE", "description": "Delete properties"},
    
    # Asset Permissions
    {"code": "ASSET_MANAGE", "description": "Manage property assets"},
    
    # Inventory/Room Permissions
    {"code": "INVENTORY_MANAGE", "description": "Manage inventory and rooms"},
    {"code": "INVENTORY_UPDATE", "description": "Update inventory availability"},
    {"code": "ROOM_UPDATE", "description": "Update room details"},
    
    # Booking Permissions
    {"code": "BOOKING_READ", "description": "View bookings"},
    {"code": "BOOKING_UPDATE", "description": "Update booking status"},
    {"code": "BOOKING_MANAGE", "description": "Full access to bookings"},
    
    # User Management Permissions
    {"code": "USER_MANAGE", "description": "Manage users (add/remove)"},
    
    # Website Content Permissions
    {"code": "WEBSITE_CONTENT_UPDATE", "description": "Update website content, images, offers"},
    
    # General Access
    {"code": "WEBSITE_ACCESS", "description": "Access the website as an end user"},
]

# Define Roles and their Permissions
ROLES = {
    "SYSTEM_ADMIN": ["*"],  # Special case: All permissions
    "PROPERTY_ADMIN": [
        "PROPERTY_READ", "PROPERTY_UPDATE", 
        "ASSET_MANAGE", 
        "INVENTORY_MANAGE", "INVENTORY_UPDATE", 
        "ROOM_UPDATE", 
        "BOOKING_READ", "BOOKING_UPDATE", "BOOKING_MANAGE",
        "USER_MANAGE"
    ],
    "PROPERTY_USER": [
        "PROPERTY_READ",
        "INVENTORY_UPDATE", 
        "ROOM_UPDATE", 
        "BOOKING_READ", "BOOKING_UPDATE"
    ],
    "WEBSITE_ADMIN": [
        "WEBSITE_CONTENT_UPDATE"
    ],
    "WEBSITE_USER": [
        "WEBSITE_ACCESS"
    ]
}

async def seed_roles():
    async with AsyncSessionLocal() as db:
        try:
            # 1. Seed Permissions
            logger.info("Seeding Permissions...")
            perm_map = {}
            for perm_data in PERMISSIONS:
                result = await db.execute(select(Permission).where(Permission.code == perm_data["code"]))
                existing_perm = result.scalars().first()
                
                if not existing_perm:
                    new_perm = Permission(code=perm_data["code"], description=perm_data["description"])
                    db.add(new_perm)
                    await db.flush()
                    perm_map[perm_data["code"]] = new_perm
                    logger.info(f"Created permission: {perm_data['code']}")
                else:
                    perm_map[perm_data["code"]] = existing_perm
                    logger.info(f"Permission already exists: {perm_data['code']}")
            
            # 2. Seed Roles
            logger.info("Seeding Roles...")
            for role_name, role_perms in ROLES.items():
                result = await db.execute(select(Role).where(Role.name == role_name))
                existing_role = result.scalars().first()
                
                if not existing_role:
                    new_role = Role(name=role_name, description=f"Default {role_name} role", is_builtin=True)
                    db.add(new_role)
                    await db.flush()
                    existing_role = new_role
                    logger.info(f"Created role: {role_name}")
                else:
                    logger.info(f"Role already exists: {role_name}")
                
                # 3. Assign Permissions to Role
                if role_perms == ["*"]:
                    # Assign ALL permissions to System Admin
                    perms_to_assign = list(perm_map.values())
                else:
                    perms_to_assign = [perm_map[code] for code in role_perms if code in perm_map]
                
                for perm in perms_to_assign:
                    # Check if mapping exists
                    result = await db.execute(
                        select(RolePermission).where(
                            RolePermission.role_id == existing_role.id,
                            RolePermission.permission_id == perm.id
                        )
                    )
                    existing_map = result.scalars().first()
                    
                    if not existing_map:
                        new_map = RolePermission(role_id=existing_role.id, permission_id=perm.id)
                        db.add(new_map)
                        logger.info(f"Assigned {perm.code} to {role_name}")
            
            await db.commit()
            logger.info("Seeding completed successfully!")
            
        except Exception as e:
            logger.error(f"Error seeding roles: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(seed_roles())
