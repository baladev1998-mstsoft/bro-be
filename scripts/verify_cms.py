import sys
import os
import asyncio
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.cms import CMSPage, CMSPageTranslation, CMSSection, CMSSectionContent

async def verify_cms():
    print("Verifying CMS data...")
    async with AsyncSessionLocal() as db:
        # Check Home Page
        result = await db.execute(
            select(CMSPage)
            .options(
                selectinload(CMSPage.translations),
                selectinload(CMSPage.sections).selectinload(CMSSection.contents)
            )
            .filter(CMSPage.slug == "home")
        )
        home = result.scalars().first()
        
        if home:
            print(f"Found Home Page: {home.id}")
            for t in home.translations:
                print(f" - Translation ({t.language_code}): {t.title}")
            
            for s in home.sections:
                print(f" - Section ({s.section_key}): {s.type}")
                for c in s.contents:
                    print(f"   - Content ({c.language_code}): {c.content}")
        else:
            print("Home Page NOT found!")

        # Check About Us Page
        result = await db.execute(
            select(CMSPage)
            .options(selectinload(CMSPage.translations))
            .filter(CMSPage.slug == "about-us")
        )
        about = result.scalars().first()
        
        if about:
            print(f"Found About Us Page: {about.id}")
            for t in about.translations:
                print(f" - Translation ({t.language_code}): {t.title}")
        else:
            print("About Us Page NOT found!")

if __name__ == "__main__":
    asyncio.run(verify_cms())
