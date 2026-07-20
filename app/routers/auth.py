from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from .. database import get_session
from .. schema import Token
from .. models import User
from .. utils import verify_password
from .. oauth2 import create_access_token

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post('/', response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)) -> Token:

    # OAuth2PasswordRequestForm is a class provided by FastAPI that automatically parses the form data sent in the request body. It expects the form data to contain two fields: username and password. In this case, we are using the username field to represent the user's email address.
    statement = select(User).where(User.email == user_credentials.username)
    results = await session.exec(statement)
    user = results.one_or_none() # only one user should be returned since email is unique
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials")    
    access_token = create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}