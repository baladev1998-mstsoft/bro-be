import asyncio
import httpx
import sys
import os
import uuid

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000/api/v1/cms"

async def test_public_api():
    unique_id = str(uuid.uuid4())[:8]
    slug = f"PubTest-{unique_id}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"1. Creating Page ({slug})...")
        response = await client.post(f"{BASE_URL}/pages", json={
            "slug": slug,
            "is_published": False,
            "parent_id": None
        })
        if response.status_code != 200:
            print(f"Failed to create page: {response.text}")
            return
        page_id = response.json()["id"]
        
        print("2. Adding Content...")
        await client.post(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "en",
            "title": "Public Test Title",
            "seo_metadata": {}
        })
        
        print("3. Publishing Page...")
        await client.post(f"{BASE_URL}/pages/{page_id}/publish")
        
        print("4. Testing GET /public/pages/{slug}...")
        response = await client.get(f"{BASE_URL}/public/pages/{slug}")
        if response.status_code == 200:
            data = response.json()
            if "versions" in data:
                print("FAILURE: 'versions' field present in public API response.")
            else:
                print("SUCCESS: 'versions' field NOT present in public API response.")
                
            if data["translations"][0]["title"] == "Public Test Title":
                print("SUCCESS: Public API returned correct content.")
            else:
                print(f"FAILURE: Content mismatch: {data['translations'][0]['title']}")
        else:
            print(f"FAILURE: Public API failed: {response.status_code} {response.text}")
            
        print("5. Testing GET /pages/{slug} (Internal API)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}")
        if response.status_code == 200:
            data = response.json()
            if "versions" in data:
                print("FAILURE: 'versions' field present in internal API response.")
            else:
                print("SUCCESS: 'versions' field NOT present in internal API response.")
        else:
            print(f"FAILURE: Internal API failed: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_public_api())
