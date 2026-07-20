import os
import asyncio

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # correct loop policy for Windows for async tests

import pytest
from fastapi import HTTPException, status
from app.oauth2 import verify_access_token

@pytest.mark.asyncio
async def test_root(async_client):
    resp = await async_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}

@pytest.mark.asyncio
async def test_create_user(raw_user_data, create_user):
    assert create_user.email == raw_user_data["email"]
    assert create_user.id is not None

@pytest.mark.asyncio
async def test_login_user(login_user):
    assert login_user.token_type == "bearer"
    assert login_user.access_token

@pytest.mark.asyncio
async def test_token_validation(create_user, login_user):
    creds_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad token")
    token_data = verify_access_token(login_user.access_token, creds_exc)
    assert token_data.id == create_user.id
    assert login_user.token_type == "bearer"

@pytest.mark.asyncio
async def test_restricted_route(authorized_client):
    resp = await authorized_client.get("/posts/")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_fail_restricted_route(async_client):
    resp = await async_client.get("/posts/")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_fail_login(async_client, raw_user_data):
    resp = await async_client.post(
        "/login/",
        data={"username": raw_user_data["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 403
