import asyncio
import httpx
import sys
import os
import uuid

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000/api/v1/cms"

async def test_versioning():
    unique_id = str(uuid.uuid4())[:8]
    slug = f"VerTest-{unique_id}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"1. Creating Page ({slug})...")
        response = await client.post(f"{BASE_URL}/pages", json={
            "slug": slug,
            "is_published": False, # Draft
            "parent_id": None
        })
        if response.status_code != 200:
            print(f"Failed to create page: {response.text}")
            return
        page_id = response.json()["id"]
        
        print("2. Adding Content (Draft)...")
        await client.post(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "en",
            "title": "Draft Title V1",
            "seo_metadata": {}
        })
        
        print("3. Fetching Public Page (Should Fail)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}")
        if response.status_code == 404:
            print("SUCCESS: Public page not found (as expected).")
        else:
            print(f"FAILURE: Public page found unexpectedly: {response.status_code}")
            
        print("4. Fetching Draft Page (Should Succeed)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}?draft=true")
        if response.status_code == 200:
            data = response.json()
            if data["translations"][0]["title"] == "Draft Title V1":
                print("SUCCESS: Draft page found with correct title.")
            else:
                print(f"FAILURE: Draft title mismatch: {data['translations'][0]['title']}")
        else:
            print(f"FAILURE: Draft page not found: {response.status_code}")
            
        print("5. Publishing Page (V1)...")
        response = await client.post(f"{BASE_URL}/pages/{page_id}/publish")
        if response.status_code == 200:
            print("SUCCESS: Page published.")
        else:
            print(f"FAILURE: Publish failed: {response.text}")
            
        print("6. Fetching Public Page (Should Succeed, V1)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}")
        if response.status_code == 200:
            data = response.json()
            if data["translations"][0]["title"] == "Draft Title V1":
                print("SUCCESS: Public page found with V1 title.")
            else:
                print(f"FAILURE: Public title mismatch: {data['translations'][0]['title']}")
        else:
            print(f"FAILURE: Public page not found after publish: {response.status_code}")
            
        print("7. Updating Content (Draft V2)...")
        await client.put(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "en",
            "title": "Draft Title V2"
        })
        
        print("8. Fetching Public Page (Should still be V1)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}")
        data = response.json()
        if data["translations"][0]["title"] == "Draft Title V1":
            print("SUCCESS: Public page is still V1.")
        else:
            print(f"FAILURE: Public page leaked V2 content: {data['translations'][0]['title']}")
            
        print("9. Fetching Draft Page (Should be V2)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}?draft=true")
        data = response.json()
        if data["translations"][0]["title"] == "Draft Title V2":
            print("SUCCESS: Draft page is V2.")
        else:
            print(f"FAILURE: Draft page mismatch: {data['translations'][0]['title']}")
            
        print("10. Publishing Page (V2)...")
        await client.post(f"{BASE_URL}/pages/{page_id}/publish")
        
        print("11. Fetching Public Page (Should be V2)...")
        response = await client.get(f"{BASE_URL}/pages/{slug}")
        data = response.json()
        if data["translations"][0]["title"] == "Draft Title V2":
            print("SUCCESS: Public page is now V2.")
        else:
            print(f"FAILURE: Public page mismatch after V2 publish: {data['translations'][0]['title']}")

if __name__ == "__main__":
    asyncio.run(test_versioning())
