from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True