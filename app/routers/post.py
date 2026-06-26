from .. models import Post, User
from .. schema import PostResponse, PostUpdate, Envelope, PostCreate
from .. database import get_session
from .. oauth2 import get_current_user


from fastapi import HTTPException, status, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from sqlmodel import select

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/")
async def get_posts(session: AsyncSession = Depends(get_session)) -> List[PostResponse]:
    statement = select(Post)
    results = await session.exec(statement)
    posts = results.all()

    return posts


# @app.post("/posts", response_model=Envelope[PostResponse], status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> PostResponse:
    new_post = Post(**post.model_dump()) # unpacking the PostCreate schema into the Post model
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    return new_post
    # return {"data": post}

    
# @app.get("/posts/{id}", response_model=Envelope[PostResponse])
@router.get("/{id}")
async def get_post(id: int, session: AsyncSession = Depends(get_session)) -> PostResponse:
    # statement = select(Post).where(Post.id == id) # When you query by a primary key index, the database does a fast index lookup (O(log n)), not a full table scan (O(n))
    # results = await session.exec(statement)
    # post = results.first()
    post = await session.get(Post, id) # This is more efficient for primary key lookups
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> None:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    await session.delete(post)
    await session.commit()

    return None

# @app.put("/posts/{id}", response_model=Envelope[PostResponse])
@router.put("/{id}")
async def update_post(id: int, updated_post: PostUpdate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> PostResponse:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    post.title = updated_post.title
    post.content = updated_post.content
    post.published = updated_post.published
    await session.commit()
    await session.refresh(post)

    return post
    
