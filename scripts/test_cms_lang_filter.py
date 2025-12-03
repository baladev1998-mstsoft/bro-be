import asyncio
import httpx
import sys
import os
import uuid

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = "http://127.0.0.1:8000/api/v1/cms"

async def test_lang_filter():
    unique_id = str(uuid.uuid4())[:8]
    slug = f"LangTest-{unique_id}"
    
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
            "title": "English Title",
            "seo_metadata": {}
        })
        
        print("3. Adding Tamil Translation...")
        await client.post(f"{BASE_URL}/pages/{page_id}/translations", json={
            "language_code": "ta",
            "title": "Tamil Title",
            "seo_metadata": {}
        })
        
        print("4. Fetching Page with lang=en...")
        response = await client.get(f"{BASE_URL}/pages/{slug}?lang=en")
        data = response.json()
        
        translations = data.get("translations", [])
        print(f"Translations found: {len(translations)}")
        if len(translations) == 1 and translations[0]["language_code"] == "en":
            print("SUCCESS: Only English translation returned.")
        else:
            print(f"FAILURE: Expected 1 'en' translation, got: {translations}")

        print("5. Fetching Page with lang=ta...")
        response = await client.get(f"{BASE_URL}/pages/{slug}?lang=ta")
        data = response.json()
        
        translations = data.get("translations", [])
        print(f"Translations found: {len(translations)}")
        if len(translations) == 1 and translations[0]["language_code"] == "ta":
            print("SUCCESS: Only Tamil translation returned.")
        else:
            print(f"FAILURE: Expected 1 'ta' translation, got: {translations}")

if __name__ == "__main__":
    asyncio.run(test_lang_filter())
