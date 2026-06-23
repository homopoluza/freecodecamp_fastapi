from sqlmodel import SQLModel, Field, func
from sqlalchemy import Boolean, Column, DateTime
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
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )