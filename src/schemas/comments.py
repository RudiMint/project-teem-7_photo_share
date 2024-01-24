from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CommentBase(BaseModel):
    """
    Base model for creating a comment.

    :param text: str: The text content of the comment.
    """
    text: str

class CommentCreate(CommentBase):
    """
    Pydantic model for creating a comment.
    Inherits from CommentBase.

    No additional attributes.
    """
    pass

class Comment(CommentBase):
    """
    Pydantic model representing a comment retrieved from the database.
    Inherits from CommentBase.

    :param id: int: The ID of the comment.
    :param user_id: int: The ID of the user who created the comment.
    :param photo_id: int: The ID of the photo associated with the comment.
    :param created_at: datetime: The timestamp indicating when the comment was created.
    :param updated_at: datetime: The timestamp indicating when the comment was last updated.

    Config:
        orm_mode (bool): Indicates that this Pydantic model is used with an ORM (SQLAlchemy) model.
    """
    id: int
    user_id: int
    photo_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
