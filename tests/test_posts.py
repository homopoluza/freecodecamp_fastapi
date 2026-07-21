from __future__ import annotations # delays the evaluation of type annotations, allowing for forward references and avoiding issues with circular imports. This is especially useful in larger projects where modules may depend on each other.

from httpx import AsyncClient
import pytest

from tests.conftest import authorized_client
from .database import testing_async_session

from app.models import Post
from app.schema import PostResponse

@pytest.mark.asyncio
async def test_get_posts(async_client: AsyncClient, test_posts: list[Post]) -> None:
    response = await async_client.get("/posts/")
    posts = response.json()
    assert len(posts) == len(test_posts)
    assert response.status_code == 200
    validated_posts = [PostResponse.model_validate(post) for post in posts]
    assert isinstance(validated_posts, list)

@pytest.mark.asyncio
async def test_get_post_non_existent(async_client: AsyncClient) -> None:
    response = await async_client.get("/posts/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "post with id 999999 was not found"}

@pytest.mark.asyncio
async def test_get_one_post(async_client: AsyncClient, test_posts: list[Post]) -> None:
    response = await async_client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200
    validated_post = PostResponse.model_validate(response.json())
    assert validated_post.id == test_posts[0].id

@pytest.mark.asyncio
async def test_create_post_authorized_client(authorized_client) -> None:
    post_data = {
        "title": "Test Post",
        "content": "This is a test post.",
    }
    response = await authorized_client.post("/posts/", json=post_data)
    assert response.status_code == 201
    created_post = PostResponse.model_validate(response.json())
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.published == True
    assert created_post.id is not None

@pytest.mark.asyncio
async def test_create_post_unauthorized_client(async_client: AsyncClient) -> None:
    post_data = {
        "title": "Test Post",
        "content": "This is a test post.",
    }
    response = await async_client.post("/posts/", json=post_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_post_unauthorized_client(async_client: AsyncClient, test_posts: list[Post]) -> None:
    response = await async_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_delete_post_authorized_client(authorized_client: AsyncClient, test_posts: list[Post]) -> None:
    response = await authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_post_non_existent(authorized_client: AsyncClient) -> None:
    response = await authorized_client.delete("/posts/999999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_post_not_owner(authorized_client: AsyncClient, test_posts: list[Post]) -> None:
    # Create a new post with a different user_id
    new_post = Post(title="Not my post", content="This is not my post.", user_id=1)
    async with testing_async_session() as session:
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)

    response = await authorized_client.delete(f"/posts/{new_post.id}")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_post_authorized_client(authorized_client: AsyncClient, test_posts: list[Post]) -> None:
    updated_data = {
        "title": "Updated Title",
        "content": "Updated content.",
        "published": False
    }
    response = await authorized_client.put(f"/posts/{test_posts[0].id}", json=updated_data)
    assert response.status_code == 200
    updated_post = PostResponse.model_validate(response.json())
    assert updated_post.title == updated_data["title"]
    assert updated_post.content == updated_data["content"]
    assert updated_post.published == updated_data["published"]

@pytest.mark.asyncio
async def test_update_post_unauthorized_client(async_client: AsyncClient, test_posts: list[Post]) -> None:
    updated_data = {
        "title": "Updated Title",
        "content": "Updated content.",
        "published": False
    }
    response = await async_client.put(f"/posts/{test_posts[0].id}", json=updated_data)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_post_not_owner(authorized_client: AsyncClient, test_posts: list[Post]) -> None:
    # Create a new post with a different user_id
    new_post = Post(title="Not my post", content="This is not my post.", user_id=1)
    async with testing_async_session() as session:
        session.add(new_post)
        await session.commit()
        await session.refresh(new_post)

    updated_data = {
        "title": "Updated Title",
        "content": "Updated content.",
        "published": False
    }
    response = await authorized_client.put(f"/posts/{new_post.id}", json=updated_data)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_post_not_exists(authorized_client: AsyncClient) -> None:
    updated_data = {
        "title": "Updated Title",
        "content": "Updated content.",
        "published": False
    }
    response = await authorized_client.put(f"/posts/999", json=updated_data)
    assert response.status_code == 404
