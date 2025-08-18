import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(".../")))
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import OperationalError
from tools.settings import settings
from tools.tools import TOOLS_CFG
import time
from sqlalchemy import text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

database_url = f"postgresql+asyncpg://{TOOLS_CFG.db_username}:{TOOLS_CFG.db_password}@{TOOLS_CFG.host}:{TOOLS_CFG.port}/{TOOLS_CFG.db_name}"
engine = create_async_engine(
    database_url,
    echo=True
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


print(f"session {AsyncSessionLocal}")
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except OperationalError as e:
            logger.error(f"Database error: {e}")
            raise


