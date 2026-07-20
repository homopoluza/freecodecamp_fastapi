from .test_database import setup_test_db, async_client
import pytest_asyncio
import uuid
from app.schema import Token, UserResponse
from app.oauth2 import verify_access_token
from fastapi import HTTPException, status

@pytest_asyncio.fixture
def raw_user_data():
    return {
        "email": f"test-{uuid.uuid4().hex}@example.com",
        "password": "pass123",
    }

@pytest_asyncio.fixture
async def create_user(async_client, raw_user_data):
    response = await async_client.post("/users/", json=raw_user_data)
    assert response.status_code == 201, response.text
    return UserResponse(**response.json())

@pytest_asyncio.fixture
async def login_user(async_client, create_user, raw_user_data):
    response = await async_client.post(
        "/login/",
        data={"username": create_user.email, "password": raw_user_data["password"]},
    )
    assert response.status_code == 200, response.text
    return Token(**response.json())

@pytest_asyncio.fixture
async def authorized_client(async_client, login_user):
    async_client.headers.update({"Authorization": f"Bearer {login_user.access_token}"})
    yield async_client
    async_client.headers.pop("Authorization", None)


# @pytest_asyncio.fixture(scope="function")
# async def authorized_user(async_client):
#     # First, create a user
#     email = f"test-{uuid.uuid4().hex}@example.com" # Generate a unique email for each test session to avoid conflicts
#     created_user = await async_client.post("/users/", json={
#         "email": email,
#         "password": "pass123"
#     })
#     assert created_user.status_code == 201, created_user.text
#     assert created_user.json()["email"] == email
#     # Then, log in
#     login = await async_client.post("/login/", data={
#         "username": email,
#         "password": "pass123"
#     })
#     assert login.status_code == 200, login.text
#     login_resp = Token(**login.json()) # Use the response from login to get the token directly
#     creds_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad token")
#     token_data = verify_access_token(login_resp.access_token, creds_exc) # Verify the token to ensure it's valid and extract the user ID
#     assert token_data.id == created_user.json()["id"]
#     assert login_resp.token_type == "bearer"
#     token = login.json()["access_token"]

#     # Inject the token into headers
#     async_client.headers.update({"Authorization": f"Bearer {token}"})
#     yield async_client
#     async_client.headers.pop("Authorization", None)