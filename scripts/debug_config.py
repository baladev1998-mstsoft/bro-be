import asyncio
import os
from app.core.config import settings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def test_async_connection(url):
    print(f"\n--- Testing Asynchronous Connection (asyncpg) ---")
    # Obfuscate password for printing
    safe_url = url
    if settings.POSTGRES_PASSWORD:
        import urllib.parse
        encoded_pwd = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD)
        safe_url = url.replace(encoded_pwd, "******")
    
    print(f"URL: {safe_url}")
    
    try:
        engine = create_async_engine(url)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"SUCCESS: Result: {result.scalar()}")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    asyncio.run(test_async_connection(settings.SQLALCHEMY_DATABASE_URI))
