import asyncio
import httpx
from app.core.config import settings

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_auth():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Login
        print("Logging in...")
        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"Login successful! Token: {access_token[:20]}...")

        # 2. Access Protected Endpoint
        print("\nAccessing protected endpoint (Amenities)...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(f"{BASE_URL}/amenities/", headers=headers)
        
        if response.status_code == 200:
            print(f"Success! Retrieved {len(response.json())} amenities.")
        else:
            print(f"Failed to access protected endpoint: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_auth())
