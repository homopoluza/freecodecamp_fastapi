from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlmodel import SQLModel

from app.config import settings
from app.main import app
from app.database import get_session

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

# Async engine
engine = create_async_engine(DATABASE_URL, echo=settings.debug)

# Async session factory
testing_async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False, # Prevents automatic expiration of objects after commit, allowing access to their attributes without needing to refresh them from the database.
)

async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with testing_async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session
        

# --- Async tests (pytest-asyncio + httpx.AsyncClient) ---
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all) # for pytest with -x, will stop the test session after the first failure. So for debugging, you might want to comment this out to inspect the database state after a failure.

    await engine.dispose() # avoid "ResourceWarning: unclosed <sqlalchemy.ext.asyncio.engine.AsyncEngine object at ...>" warning and resource leak

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

 
# client = TestClient(app)  # kept for reference (sync TestClient flow)

# @pytest.fixture(scope="session", autouse=True) # This fixture will run once per test session, automatically setting up and tearing down the test database.
# def setup_test_db(): 
#     async def create_tables(): # async subfunction cause pytest fixtures cannot be async and db session is async
#             async with engine.begin() as conn:
#                 await conn.run_sync(SQLModel.metadata.create_all)

#     asyncio.run(create_tables())
#     yield

#     async def drop_tables():
#         async with engine.begin() as conn:
#             await conn.run_sync(SQLModel.metadata.drop_all)

#     asyncio.run(drop_tables())
#     asyncio.run(engine.dispose())
