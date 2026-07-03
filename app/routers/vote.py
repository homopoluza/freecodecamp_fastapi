from .. models import User, Vote, Post
from .. schema import VoteSchema, VoteDirection
from .. database import get_session
from .. oauth2 import get_current_user

from fastapi import HTTPException, status, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

router = APIRouter(
    prefix="/votes",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: VoteSchema, session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):

    post = await session.get(Post, vote.post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exist.")
    
    vote_query = select(Vote).where(Vote.post_id == vote.post_id, Vote.user_id == current_user.id)
    result = await session.exec(vote_query)
    existing_vote = result.first()

    if vote.dir == VoteDirection.UP:
        # Check if the user has already voted for this post   
        if existing_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already voted for this post.")

        # Create a new vote
        new_vote = Vote(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        await session.commit()
        return {"message": "Successfully added vote."}
    
    else:
        if not existing_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist.")
        
        await session.delete(existing_vote)
        await session.commit()

        return {"message": "Successfully removed vote."}