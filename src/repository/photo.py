from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Photo, User, Tag, PhotoTag, Role
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


async def update_photo(photo_id: int, description, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo:
        print(user.role.value)
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to edit this photo"
            )
        photo.description = description
        await db.commit()
        await db.refresh(photo)
    return photo


async def delete_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.user_id != user.id and user.role != Role.admin:
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this photo"
            )
        await db.delete(photo)
        await db.commit()
        return {"message": f"Photo with ID {photo_id} deleted successfully"}
    raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found")


async def get_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    todo = await db.execute(stmt)
    return todo.scalar_one_or_none()
