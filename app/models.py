from sqlmodel import SQLModel, Relationship, Field, func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from datetime import datetime

class Post(SQLModel, table = True):
    __tablename__ = "posts"
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    published: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False, server_default="True")
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True),
        nullable=False,
        server_default=func.now())
        )
    user_id: int = Field(
            sa_column=Column(
                Integer,
                ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False
            )
    )
    user: User = Relationship()

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    #email: str = Field(sa_column=Column(String, nullable=False, unique=True)) # index=True is not needed because unique=True automatically creates an index
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), 
            nullable=False, 
            server_default=func.now()
            )
        )
    
class Vote(SQLModel, table=True):
    __tablename__ = "votes"
    user_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True
        )
    )
    post_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("posts.id", ondelete="CASCADE"),
            primary_key=True
        )
    )