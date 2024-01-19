from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Photo, User, Tag, PhotoTag
from src.schemas.photo import PhotoSchema, PhotoUpdateSchema, PhotoResponse


async def create_photo_info(description: str, tags, db: AsyncSession, user: User, image_path):
    if tags is not None:
        new_tag_list = tags[0].split(',')
        if len(new_tag_list) > 5:
            error_message = "Too many tags. Maximum is 5."
            raise HTTPException(status_code=400, detail=error_message)
        for tag in new_tag_list:
            stmt = select(Tag).filter_by(name=tag)
            result = await db.execute(stmt)
            check_tag = result.scalar_one_or_none()
            if not check_tag:
                db_tag = Tag(name=tag)
                db.add(db_tag)
    photo = Photo(description=description, image_path=image_path,
                  user=user)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def get_all_photos(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Photo).offset(offset).limit(limit).filter_by(user=user)
    photos = await db.execute(stmt)
    photos_for_scheme = photos.scalars().all()
    if photos_for_scheme:
        return photos_for_scheme
    return {"message": "You haven't uploaded any photos yet"}