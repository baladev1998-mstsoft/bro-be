import asyncio
import httpx
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import uuid

BASE_URL = "http://127.0.0.1:8000/api/v1/cms"

async def test_cms_flow():
    unique_id = str(uuid.uuid4())[:8]
    parent_slug = f"Service-{unique_id}"
    child_slug = f"Consulting-{unique_id}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        print(f"1. Creating Parent Page ({parent_slug})...")
        response = await client.post(f"{BASE_URL}/pages", json={
            "slug": parent_slug,
            "is_published": True,
            "parent_id": None
        })
        if response.status_code != 200:
            print(f"Failed to create parent page: {response.text}")
            return
        parent_page = response.json()
        parent_id = parent_page["id"]
        print(f"Parent Page Created: {parent_id}")

        print(f"\n2. Creating Child Page ({child_slug})...")
        response = await client.post(f"{BASE_URL}/pages", json={
            "slug": child_slug,
            "is_published": True,
            "parent_id": parent_id
        })
        if response.status_code != 200:
            print(f"Failed to create child page: {response.text}")
            return
        child_page = response.json()
        child_id = child_page["id"]
        print(f"Child Page Created: {child_id}")

        print("\n3. Adding Translation to Child Page...")
        response = await client.post(f"{BASE_URL}/pages/{child_id}/translations", json={
            "language_code": "en",
            "title": "Consulting Services",
            "seo_metadata": {"title": "Consulting"}
        })
        if response.status_code != 200:
            print(f"Failed to add translation: {response.text}")
            return
        print("Translation Added")

        print("\n4. Adding Section to Child Page...")
        response = await client.post(f"{BASE_URL}/pages/{child_id}/sections", json={
            "section_key": "intro",
            "type": "text",
            "order_index": 0,
            "is_active": True
        })
        if response.status_code != 200:
            print(f"Failed to add section: {response.text}")
            return
        section = response.json()
        section_id = section["id"]
        print(f"Section Added: {section_id}")

        print("\n5. Adding Content to Section...")
        response = await client.post(f"{BASE_URL}/sections/{section_id}/content", json={
            "language_code": "en",
            "content": {"text": "We offer great consulting."}
        })
        if response.status_code != 200:
            print(f"Failed to add content: {response.text}")
            return
        print("Content Added")

        print(f"\n6. Fetching Parent Page ({parent_slug}) - Expecting Child with Details...")
        # This is where the error occurred: accessing children.translations/sections
        response = await client.get(f"{BASE_URL}/pages/{parent_slug}?lang=en")
        if response.status_code == 200:
            data = response.json()
            print("Successfully fetched Parent Page!")
            # Verify child details are present
            if data["children"]:
                child = data["children"][0]
                print(f"Child found: {child['slug']}")
                if "translations" in child:
                    print(f"Child translations: {len(child['translations'])}")
                else:
                    print("Child translations MISSING")
            else:
                print("No children found (unexpected)")
        else:
            print(f"FAILED to fetch Parent Page: {response.text}")

        print("\n7. Fetching Pages List with Parent ID...")
        response = await client.get(f"{BASE_URL}/pages?parent_id={parent_id}")
        if response.status_code == 200:
             print("Successfully fetched Pages List!")
        else:
             print(f"FAILED to fetch Pages List: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_cms_flow())
