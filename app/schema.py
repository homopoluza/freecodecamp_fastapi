from sqlmodel import SQLModel
from datetime import datetime
from pydantic.generics import GenericModel
from pydantic import EmailStr, conint
from typing import Generic, TypeVar
from enum import Enum

T = TypeVar('T')

class PostResponse(SQLModel):
    id: int
    title: str
    content: str
    created_at: datetime
    published: bool = True
    user_id: int
    user: UserResponse

class PostCreate(SQLModel):
    title: str
    content: str
    published: bool = True

class PostUpdate(SQLModel):
    title: str
    content: str
    published: bool = True

class PostWithVotes(PostResponse):
    votes: int

# class PostResponse(SQLModel):
#     data: PostRead

# it will return the same data as PostRead but wrapped in a "data" key, which is a common convention for API responses.
# {
#   "data": {
#     "id": ...,
#     "title": ...,
#     "content": ...,
#     "published": ...,
#     "created_at": ...
#   }
# } This allows for a consistent response structure and makes it easier to add additional metadata or fields in the future without changing the existing data format.

class Envelope(GenericModel, Generic[T]):
    data: T

# The Envelope class is a generic wrapper that can be used to standardize API responses. By using a generic type T, it allows you to wrap any type of data in a consistent structure. For example, you could use Envelope[PostRead] to wrap a PostRead object, or Envelope[List[PostRead]] to wrap a list of PostRead objects. This approach promotes consistency in your API responses and makes it easier to manage and extend your response formats in the future.

class UserCreate(SQLModel):
    email: EmailStr
    password: str

class UserResponse(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id: int | None = None

class VoteDirection(int, Enum):
    DOWN = 0
    UP = 1

class VoteSchema(SQLModel):
    post_id: int
    dir: VoteDirection