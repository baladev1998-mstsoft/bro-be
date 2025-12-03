import logging
import sys
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Add backend directory to path
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import AsyncSessionLocal
from app.models.cms import CMSPage, CMSPageTranslation, CMSSection, CMSSectionContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_cms():
    logger.info("Seeding CMS data...")
    
    async with AsyncSessionLocal() as db:
        # 1. Home Page
        result = await db.execute(select(CMSPage).filter(CMSPage.slug == "home"))
        home_page = result.scalars().first()
        
        if not home_page:
            home_page = CMSPage(slug="home", is_published=True)
            db.add(home_page)
            await db.commit()
            await db.refresh(home_page)
            logger.info("Created Home page")
        
        # Translations for Home
        result = await db.execute(select(CMSPageTranslation).filter(
            CMSPageTranslation.page_id == home_page.id, 
            CMSPageTranslation.language_code == "en"
        ))
        if not result.scalars().first():
            db.add(CMSPageTranslation(
                page_id=home_page.id,
                language_code="en",
                title="Home",
                seo_metadata={"title": "Welcome to BRO", "description": "Best Real Estate & Travel"}
            ))
        
        result = await db.execute(select(CMSPageTranslation).filter(
            CMSPageTranslation.page_id == home_page.id, 
            CMSPageTranslation.language_code == "ta"
        ))
        if not result.scalars().first():
            db.add(CMSPageTranslation(
                page_id=home_page.id,
                language_code="ta",
                title="முகப்பு",
                seo_metadata={"title": "BRO-விற்கு வருக", "description": "சிறந்த ரியல் எஸ்டேட் மற்றும் பயணம்"}
            ))
        
        # Sections for Home
        # Hero Section
        result = await db.execute(select(CMSSection).filter(
            CMSSection.page_id == home_page.id, 
            CMSSection.section_key == "hero"
        ))
        hero_section = result.scalars().first()
        
        if not hero_section:
            hero_section = CMSSection(
                page_id=home_page.id,
                section_key="hero",
                type="hero",
                order_index=1
            )
            db.add(hero_section)
            await db.commit()
            await db.refresh(hero_section)

        # Hero Content
        result = await db.execute(select(CMSSectionContent).filter(
            CMSSectionContent.section_id == hero_section.id, 
            CMSSectionContent.language_code == "en"
        ))
        if not result.scalars().first():
            db.add(CMSSectionContent(
                section_id=hero_section.id,
                language_code="en",
                content={
                    "headline": "Find Your Dream Property",
                    "subheadline": "We help you find the best properties in town.",
                    "cta_text": "Explore Now",
                    "cta_link": "/properties"
                }
            ))
        
        result = await db.execute(select(CMSSectionContent).filter(
            CMSSectionContent.section_id == hero_section.id, 
            CMSSectionContent.language_code == "ta"
        ))
        if not result.scalars().first():
            db.add(CMSSectionContent(
                section_id=hero_section.id,
                language_code="ta",
                content={
                    "headline": "உங்கள் கனவு சொத்தை தேடுங்கள்",
                    "subheadline": "நகரத்தில் சிறந்த சொத்துக்களைக் கண்டறிய நாங்கள் உதவுகிறோம்.",
                    "cta_text": "இப்போது ஆராயுங்கள்",
                    "cta_link": "/properties"
                }
            ))

        # 2. About Us Page
        result = await db.execute(select(CMSPage).filter(CMSPage.slug == "about-us"))
        about_page = result.scalars().first()
        
        if not about_page:
            about_page = CMSPage(slug="about-us", is_published=True)
            db.add(about_page)
            await db.commit()
            await db.refresh(about_page)
            logger.info("Created About Us page")

        # Translations for About Us
        result = await db.execute(select(CMSPageTranslation).filter(
            CMSPageTranslation.page_id == about_page.id, 
            CMSPageTranslation.language_code == "en"
        ))
        if not result.scalars().first():
            db.add(CMSPageTranslation(
                page_id=about_page.id,
                language_code="en",
                title="About Us",
                seo_metadata={"title": "About BRO", "description": "Who we are"}
            ))

        result = await db.execute(select(CMSPageTranslation).filter(
            CMSPageTranslation.page_id == about_page.id, 
            CMSPageTranslation.language_code == "ta"
        ))
        if not result.scalars().first():
            db.add(CMSPageTranslation(
                page_id=about_page.id,
                language_code="ta",
                title="எங்களைப் பற்றி",
                seo_metadata={"title": "BRO பற்றி", "description": "நாங்கள் யார்"}
            ))

        await db.commit()
        logger.info("CMS seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_cms())
