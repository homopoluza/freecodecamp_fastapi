from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import TypedDict

from .database import async_client, testing_async_session, setup_test_db
import pytest_asyncio
import uuid
from app.schema import Token, UserResponse
from app.models import Post
from app.oauth2 import verify_access_token
from fastapi import HTTPException, status
from httpx import AsyncClient

import os
import asyncio

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # correct loop policy for Windows for async tests


class RawUserData(TypedDict):
    email: str
    password: str


@pytest_asyncio.fixture
def raw_user_data() -> RawUserData:
    return {
        "email": f"test-{uuid.uuid4().hex}@example.com",
        "password": "pass123",
    }


@pytest_asyncio.fixture
async def create_user(async_client: AsyncClient, raw_user_data: RawUserData) -> UserResponse:
    response = await async_client.post("/users/", json=raw_user_data)
    assert response.status_code == 201, response.text
    return UserResponse(**response.json())


@pytest_asyncio.fixture
async def login_user(async_client: AsyncClient, create_user: UserResponse, raw_user_data: RawUserData) -> Token:
    response = await async_client.post(
        "/login/",
        data={"username": create_user.email, "password": raw_user_data["password"]},
    )
    assert response.status_code == 200, response.text
    return Token(**response.json())


@pytest_asyncio.fixture
async def authorized_client(async_client: AsyncClient, login_user: Token) -> AsyncGenerator[AsyncClient, None]:
    async_client.headers.update({"Authorization": f"Bearer {login_user.access_token}"})
    yield async_client
    async_client.headers.pop("Authorization", None)


@pytest_asyncio.fixture
async def test_posts(create_user: UserResponse) -> list[Post]:
    post_payloads: list[dict[str, str]] = [
        {"title": "Test Post 1", "content": "This is a test post 1."},
        {"title": "Test Post 2", "content": "This is a test post 2."},
        {"title": "Test Post 3", "content": "This is a test post 3."},
    ]
    posts = [Post(user_id=create_user.id, **payload) for payload in post_payloads]

    async with testing_async_session() as session:
        session.add_all(posts)
        await session.commit()
        for post in posts:
            await session.refresh(post)

    return posts

# @pytest_asyncio.fixture
# async def test_posts(authorized_client, create_user):
#     # post_data = [{
#     #     "title": "Test Post 1",
#     #     "content": "This is a test post 1.",
#     #     "user_id": create_user.id
#     # },
#     #     {
#     #     "title": "Test Post 2",
#     #     "content": "This is a test post 2.",
#     #     "user_id": create_user.id
#     # },
#     #     {
#     #     "title": "Test Post 3",
#     #     "content": "This is a test post 3.",
#     #     "user_id": create_user.id
#     # }]
#     post_data = {
#         "title": "Test Post 1",
#         "content": "This is a test post 1.",
#         "user_id": create_user.id
#     }
#     response = await authorized_client.post("/posts/", json=post_data)
#     assert response.status_code == 201, response.text
#     return response.json()


@pytest_asyncio.fixture(scope="function")
async def authorized_user_2(async_client):
    # First, create a user
    email = f"test-{uuid.uuid4().hex}@example.com" # Generate a unique email for each test session to avoid conflicts
    created_user = await async_client.post("/users/", json={
        "email": email,
        "password": "pass123"
    })
    assert created_user.status_code == 201, created_user.text
    assert created_user.json()["email"] == email
    # Then, log in
    login = await async_client.post("/login/", data={
        "username": email,
        "password": "pass123"
    })
    assert login.status_code == 200, login.text
    login_resp = Token(**login.json()) # Use the response from login to get the token directly
    creds_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad token")
    token_data = verify_access_token(login_resp.access_token, creds_exc) # Verify the token to ensure it's valid and extract the user ID
    assert token_data.id == created_user.json()["id"]
    assert login_resp.token_type == "bearer"
    token = login.json()["access_token"]

    # Inject the token into headers
    async_client.headers.update({"Authorization": f"Bearer {token}"})
    yield async_client
    async_client.headers.pop("Authorization", None)