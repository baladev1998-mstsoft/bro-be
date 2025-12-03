import asyncio
import httpx
import sys
import os
import uuid

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000/api/v1/cms"

async def test_put_apis():
    unique_id = str(uuid.uuid4())[:8]
    slug = f"PutTest-{unique_id}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"1. Creating Page ({slug})...")
        response = await client.post(f"{BASE_URL}/pages", json={
            "slug": slug,
            "is_published": True,
            "parent_id": None
        })
        page_id = response.json()["id"]
        
        print("2. Adding English Translation...")
        await client.post(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "en",
            "title": "Original Title",
            "seo_metadata": {}
        })
        
        print("3. Adding Section...")
        response = await client.post(f"{BASE_URL}/pages/{page_id}/sections", json={
            "section_key": "hero",
            "type": "text",
            "order_index": 0,
            "is_active": True
        })
        section_id = response.json()["id"]
        
        print("4. Adding Section Content...")
        await client.post(f"{BASE_URL}/sections/{section_id}/content", json={
            "language_code": "en",
            "content": {"text": "Original Content"}
        })
        
        print("\n--- Testing PUT APIs ---")
        
        print("5. Updating Translation (PUT)...")
        response = await client.put(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "en",
            "title": "Updated Title"
        })
        if response.status_code == 200:
            data = response.json()
            if data["title"] == "Updated Title":
                print("SUCCESS: Translation updated.")
            else:
                print(f"FAILURE: Title mismatch: {data['title']}")
        else:
            print(f"FAILURE: {response.text}")
            
        print("6. Updating Section (PUT)...")
        response = await client.put(f"{BASE_URL}/pages/{page_id}/sections", json={
            "section_key": "hero",
            "order_index": 5
        })
        if response.status_code == 200:
            data = response.json()
            if data["order_index"] == 5:
                print("SUCCESS: Section updated.")
            else:
                print(f"FAILURE: Order index mismatch: {data['order_index']}")
        else:
            print(f"FAILURE: {response.text}")
            
        print("7. Updating Section Content (PUT)...")
        response = await client.put(f"{BASE_URL}/sections/{section_id}/content", json={
            "language_code": "en",
            "content": {"text": "Updated Content"}
        })
        if response.status_code == 200:
            data = response.json()
            if data["content"]["text"] == "Updated Content":
                print("SUCCESS: Content updated.")
            else:
                print(f"FAILURE: Content mismatch: {data['content']}")
        else:
            print(f"FAILURE: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_put_apis())
