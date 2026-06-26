from .. models import User
from .. schema import UserCreate, UserResponse
from .. utils import hash_password
from .. database import get_session

from fastapi import Body, FastAPI, HTTPException, status, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)) -> UserResponse: 
    user.password = hash_password(user.password)
    new_user = User(**user.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

@router.get("/{id}" )
async def get_user(id: int, session: AsyncSession = Depends(get_session)) -> UserResponse:
    user = await session.get(User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} was not found")
    
    return user