import time
import logging
from typing import List, Optional
from unittest import result
from fastapi import Body, FastAPI, HTTPException, status, Depends
from pwdlib import PasswordHash
from pydantic import BaseModel
import psycopg
from psycopg.rows import dict_row
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from .database import get_session, init_db, close_db
from .models import Post, User
from .schema import PostResponse, PostUpdate, Envelope, PostCreate, UserCreate, UserResponse
from .utils import hash_password

logger = logging.getLogger("uvicorn.error")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    await init_db()
    yield       
    await close_db()  # Shutdown code (optional)

app = FastAPI(lifespan=lifespan)        

# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool = True

while True:
    try:
        with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                logger.info("Database connection was successful!")
                break
    except Exception as e:
        logger.error("Database connection failed:", e)


@app.get("/")
async def root():
    return {"message": "Hello World!!!"}

@app.get("/posts")
async def get_posts(session: AsyncSession = Depends(get_session)) -> List[PostResponse]:
    statement = select(Post)
    results = await session.exec(statement)
    posts = results.all()
    return posts
# async def get_posts() -> dict:
#     with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
#         with conn.cursor(row_factory=dict_row) as cur:
#             cur.execute("SELECT * FROM posts")
#             posts = cur.fetchall()
#     return {"data": posts}


# @app.post("/posts", response_model=Envelope[PostResponse], status_code=status.HTTP_201_CREATED)
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, session: AsyncSession = Depends(get_session)) -> PostResponse:
    new_post = Post(**post.model_dump()) # unpacking the PostCreate schema into the Post model
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    return new_post
    # return {"data": post}
# async def create_post(post: Post) -> dict: 
#     with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
#         with conn.cursor(row_factory=dict_row) as cur:
#             cur.execute("""
#                 INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
#                 (post.title, post.content, post.published))
#             new_post = cur.fetchone()
#             conn.commit()
#     return {"data": new_post}

    
# @app.get("/posts/{id}", response_model=Envelope[PostResponse])
@app.get("/posts/{id}")
async def get_post(id: int, session: AsyncSession = Depends(get_session)) -> PostResponse:
    # statement = select(Post).where(Post.id == id) # When you query by a primary key index, the database does a fast index lookup (O(log n)), not a full table scan (O(n))
    # results = await session.exec(statement)
    # post = results.first()
    post = await session.get(Post, id) # This is more efficient for primary key lookups
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    return post
# async def get_post(id: int) -> dict:
#     with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
#         with conn.cursor(row_factory=dict_row) as cur:
#             cur.execute("""SELECT * FROM posts WHERE id = %s""", (id,))
#             post = cur.fetchone()
#             if not post:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
#     return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, session: AsyncSession = Depends(get_session)) -> None:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    await session.delete(post)
    logger.info("delete_post called for id=%s", id)
    await session.commit()
    return None
    # with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
    #     with conn.cursor(row_factory=dict_row) as cur:
    #         cur.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    #         deleted_post = cur.fetchone()
    #         conn.commit()
    #         if not deleted_post:
    #             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")

# @app.put("/posts/{id}", response_model=Envelope[PostResponse])
@app.put("/posts/{id}")
async def update_post(id: int, updated_post: PostUpdate, session: AsyncSession = Depends(get_session)) -> PostResponse:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    post.title = updated_post.title
    post.content = updated_post.content
    post.published = updated_post.published
    await session.commit()
    await session.refresh(post)
    return post
    
    # with psycopg.connect("dbname=fastapi user=postgres password='romumne' host=localhost port=5432") as conn:
    #     with conn.cursor(row_factory=dict_row) as cur:
    #         cur.execute("""
    #             UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
    #             (updated_post.title, updated_post.content, updated_post.published, id))
    #         updated_post = cur.fetchone()
    #         conn.commit()
    # if not updated_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    # return {"data": updated_post}
@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)) -> UserResponse: 
    user.password = hash_password(user.password)
    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@app.get("/users/{id}")
async def get_user(id: int, session: AsyncSession = Depends(get_session)) -> UserResponse:
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} was not found")
    return user