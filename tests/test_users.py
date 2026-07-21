from __future__ import annotations

from typing import TypedDict

import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient

from app.oauth2 import verify_access_token
from app.schema import Token, UserResponse


class UserPayload(TypedDict):
    email: str
    password: str


@pytest.mark.asyncio
async def test_root(async_client: AsyncClient) -> None:
    resp = await async_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}


@pytest.mark.asyncio
async def test_create_user(raw_user_data: UserPayload, create_user: UserResponse) -> None:
    assert create_user.email == raw_user_data["email"]
    assert create_user.id is not None


@pytest.mark.asyncio
async def test_login_user(login_user: Token) -> None:
    assert login_user.token_type == "bearer"
    assert login_user.access_token


@pytest.mark.asyncio
async def test_token_validation(create_user: UserResponse, login_user: Token) -> None:
    creds_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad token")
    token_data = verify_access_token(login_user.access_token, creds_exc)
    assert token_data.id == create_user.id
    assert login_user.token_type == "bearer"

# @pytest.mark.asyncio
# async def test_restricted_route(authorized_client):
#     resp = await authorized_client.get("/posts/")
#     assert resp.status_code == 200

# @pytest.mark.asyncio
# async def test_fail_restricted_route(async_client):
#     resp = await async_client.get("/posts/")
#     assert resp.status_code == 401


@pytest.mark.parametrize("email, password, status_code", [
    ("test@example.com", "wrongpassword", 403),
    (None, "password123", 422),
    ("test@example.com", None, 422)])
@pytest.mark.asyncio
async def test_fail_login(async_client: AsyncClient, email: str | None, password: str | None, status_code: int) -> None:
    resp = await async_client.post(
        "/login/",
        data={"username": email, "password": password},
    )
    assert resp.status_code == status_code
