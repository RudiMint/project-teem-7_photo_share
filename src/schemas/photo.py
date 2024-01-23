from datetime import datetime
from typing import List

from pydantic import BaseModel


class PhotoResponse(BaseModel):
    id: int = 1
    image_path: str
    description: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class PhotoWithNameSchema(PhotoResponse):
    tags: List[str]


class PhotoInfo(BaseModel):
    photo_id: int
    username: str
    image_path: str
    description: str
    tags: List[str]


class TransformResult(BaseModel):
    photo_id: int
    new_image_path: str
    description: str
    created_at: datetime | None
    updated_at: datetime | None
