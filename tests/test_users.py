import os
import asyncio

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # correct loop policy for Windows for async tests

from app.database import get_session, init_db, close_db
from app.main import app
from fastapi.testclient import TestClient
from app.schema import UserResponse
from app.config import settings
from contextlib import asynccontextmanager
import pytest

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlmodel import SQLModel

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


client = TestClient(app)

@pytest.fixture(scope="session", autouse=True) # This fixture will run once per test session, automatically setting up and tearing down the test database.
def setup_test_db(): 
    async def create_tables(): # async subfunction cause pytest fixtures cannot be async and db session is async
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

    asyncio.run(create_tables())
    yield

    async def drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    asyncio.run(drop_tables())
    asyncio.run(engine.dispose())

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    response = client.post("/users/", json={"email": "test@example.com", "password": "pass123"})
    new_user = UserResponse(**response.json())
    assert new_user.email == "test@example.com"
    assert response.status_code == 201