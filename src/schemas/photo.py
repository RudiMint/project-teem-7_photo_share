from datetime import datetime
from typing import List

from pydantic import BaseModel, Field



class PhotoSchema(BaseModel):
    description: str = Field(min_length=3, max_length=250)
    tags: List[str] | None = Field()


class PhotoUpdateSchema(PhotoSchema):
    description: str = Field(min_length=3, max_length=250)


class PhotoResponse(BaseModel):
    id: int = 1
    image_path: str
    description: str
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True