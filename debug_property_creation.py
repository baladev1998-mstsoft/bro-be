import asyncio
import uuid
from app.db.session import AsyncSessionLocal
from app import services, schemas, models

async def debug_create_property():
    async with AsyncSessionLocal() as db:
        # Fetch a destination
        dest_result = await services.destination_service.get_multi(db, limit=1)
        if not dest_result:
            print("No destinations found.")
            return
        dest_id = dest_result[0].id
        print(f"Using Destination ID: {dest_id}")

        # Create Property
        property_in = schemas.PropertyCreate(
            name="Debug Property",
            slug=f"debug-property-{uuid.uuid4()}",
            property_type="hotel",
            address="Debug Address",
            contact_email="debug@example.com",
            contact_phone="1234567890",
            overview="Debug Overview",
            rating=4.5,
            is_published=False,
            destination_id=dest_id
        )

        print("Attempting to create property...")
        try:
            prop = await services.property_service.create(db=db, obj_in=property_in)
            print(f"Property created successfully: {prop.id}")
        except Exception as e:
            print(f"Error creating property: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_create_property())
