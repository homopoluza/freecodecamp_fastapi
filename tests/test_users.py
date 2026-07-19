import os
import asyncio

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # correct loop policy for Windows for async tests

from app.database import get_session
from app.main import app
from app.schema import UserResponse
from app.config import settings

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from sqlmodel import SQLModel

DATABASE_URL = f'postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'

# Async engine
engine = create_async_engine(DATABASE_URL, echo=settings.debug)
        
 
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



# def test_root():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World"}

# def test_create_user():
#     response = client.post("/users/", json={"email": "test@example.com", "password": "pass123"})
#     new_user = UserResponse(**response.json())
#     assert new_user.email == "test@example.com"
#     assert response.status_code == 201


# --- Async tests (pytest-asyncio + httpx.AsyncClient) ---
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all) # for pytest with -x, will stop the test session after the first failure. So for debugging, you might want to comment this out to inspect the database state after a failure.
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture(scope="session")
async def authorized_client(async_client):
    # First, create a user
    await async_client.post("/users/", json={
        "email": "test@example.com",
        "password": "pass123"
    })

    # Then, log in
    login_resp = await async_client.post("/login", data={
        "username": "test@example.com",
        "password": "pass123"
    })
    token = login_resp.json()["access_token"]

    # Inject the token into headers
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    yield async_client

@pytest.mark.asyncio
async def test_root(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_create_user(async_client):
    resp = await async_client.post("/users/", json={"email": "test@example.com", "password": "pass123"})
    new_user = UserResponse(**resp.json())
    assert new_user.email == "test@example.com"
    assert resp.status_code == 201

# @pytest.mark.asyncio
# async def test_protected_route(authorized_client):
#     resp = await authorized_client.get("/protected-route")
#     assert resp.status_code == 200
