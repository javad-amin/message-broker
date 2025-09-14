from typing import AsyncIterator

import pytest_asyncio

from app.database.db import Base, engine


@pytest_asyncio.fixture(autouse=True, scope="function")
async def init_db() -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
