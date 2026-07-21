from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.models import Post, Vote
from .database import testing_async_session as session_factory # it tried to resolve it as a pytest fixture


@pytest_asyncio.fixture
async def test_vote(test_posts: list[Post], create_user) -> Vote:
    new_vote = Vote(user_id=create_user.id, post_id=test_posts[0].id)
    async with session_factory() as session:
        session.add(new_vote)
        await session.commit()
        await session.refresh(new_vote)
    return new_vote


@pytest.mark.asyncio
async def test_vote_on_post(authorized_client: AsyncClient, test_posts: list[Post]) -> None:
    post_id = test_posts[0].id
    response = await authorized_client.post("/votes/", json={"post_id": post_id, "dir": 1})
    assert response.status_code == 201
    assert response.json() == {"message": "Successfully added vote."}


@pytest.mark.asyncio
async def test_vote_on_post_unauthorized(async_client: AsyncClient, test_posts: list[Post]) -> None:
    post_id = test_posts[0].id
    response = await async_client.post("/votes/", json={"post_id": post_id, "dir": 1})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_vote_twice_on_post(authorized_client: AsyncClient, test_posts: list[Post], test_vote: Vote) -> None:
    response = await authorized_client.post("/votes/", json={"post_id": test_posts[0].id, "dir": 1})
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_delete_vote(authorized_client: AsyncClient, test_posts: list[Post], test_vote: Vote) -> None:
    response = await authorized_client.post("/votes/", json={"post_id": test_posts[0].id, "dir": 0})
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_delete_vote_not_exists(authorized_client: AsyncClient) -> None:
    response = await authorized_client.post("/votes/", json={"post_id": 99999, "dir": 0})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_vote_on_post_not_exists(authorized_client: AsyncClient) -> None:
    response = await authorized_client.post("/votes/", json={"post_id": 9999, "dir": 1})
    assert response.status_code == 404
