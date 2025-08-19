import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(".../")))
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import OperationalError
from tools.tools import TOOLS_CFG
from typing import AsyncIterator
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


database_url = f"postgresql+asyncpg://{TOOLS_CFG.db_username}:{TOOLS_CFG.db_password}@{TOOLS_CFG.host}:{TOOLS_CFG.port}/{TOOLS_CFG.db_name}"
engine = create_async_engine(
    database_url,
    echo=True
)
print(database_url)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

async def get_db()-> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            print("Database connection established")
            yield session
        except OperationalError as e:
            logger.error(f"Database error: {e}")
            raise
        
async def test_connection():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Connection OK:", result.scalar())
    except Exception as e:
        logger.error(f"Failed to connect to DB: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())


