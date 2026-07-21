from re import search

from .. models import Post, User, Vote
from .. schema import PostResponse, PostUpdate, Envelope, PostCreate
from .. database import get_session
from .. oauth2 import get_current_user


from fastapi import HTTPException, status, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from typing import List
from sqlmodel import select, func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/")
async def get_posts(session: AsyncSession = Depends(get_session), limit: int = 10, skip: int = 0, search: str = "") -> List[PostResponse]:
    statement = (
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Post.id == Vote.post_id, isouter=True)
        .options(selectinload(Post.user))
        .filter(Post.title.ilike(f"%{search}%") | Post.content.ilike(f"%{search}%"))
        .group_by(Post.id)
        .limit(limit)
        .offset(skip)
    )
    results = await session.exec(statement)
    rows = results.all() # returns a list of tuples, where each tuple contains a Post object and the corresponding vote count. (Post, votes)

    return [
        PostResponse(
            **post.model_dump(),
            user=post.user, # post.model_dump() gives you a dict of the Post fields, but it usually does not include related fields like user unless you explicitly dump them. That’s why user=post.user is needed.
            votes=votes,
        )
        for post, votes in rows
    ]


# @app.post("/posts", response_model=Envelope[PostResponse], status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> PostResponse:
    new_post = Post(user_id=current_user.id, **post.model_dump()) # unpacking the PostCreate schema into the Post model
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
    # statement = (
    #     select(Post)
    #     .where(Post.id == id)
    #     .options(joinedload(Post.user))  # eager-load user
    # )
    # post = await session.get(Post, id) # This is more efficient for primary key lookups. Doesn't work with joinedload, so we use the select statement above instead.
    statement = (
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Post.id == Vote.post_id, isouter=True)
        .options(selectinload(Post.user)) # 2 queries instead of 1 query with a join, but it’s more efficient for large datasets because it avoids the Cartesian product problem. It fetches the posts and their users in one query, and then fetches the votes in a separate query. Plus, joinedload doesn't work here anyway because we are using an aggregate function (count) which requires a group by clause, and joinedload doesn't support that.
        .where(Post.id == id)
        .group_by(Post.id)
        )

    result = await session.exec(statement)
    post = result.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    
    post, votes = post # unpack the tuple returned by the query into the Post object and the vote count

    return PostResponse(
        **post.model_dump(),
        user=post.user, # post.model_dump() gives you a dict of the Post fields, but it usually does not include related fields like user unless you explicitly dump them. That’s why user=post.user is needed.
        votes=votes,
    )



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> None:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} was not found")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to delete this post")
    
    await session.delete(post)
    await session.commit()

    return None

# @app.put("/posts/{id}", response_model=Envelope[PostResponse])
@router.put("/{id}")
async def update_post(id: int, updated_post: PostUpdate, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)) -> PostResponse:
    post = await session.get(Post, id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to update this post")

    post.title = updated_post.title
    post.content = updated_post.content
    post.published = updated_post.published
    await session.commit()
    await session.refresh(post)

    return post

