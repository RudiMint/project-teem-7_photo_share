from cloudinary import utils
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from src.database.models import Photo, User, Tag, PhotoTag
from src.schemas.photo import PhotoInfo, TransformResult


async def create_photo_info(description: str, tags, db: AsyncSession, user: User, image_path):
    new_tag_list = None
    tag_names = []
    if tags[0].strip():
        new_tag_list = tags[0].split(',')
        if len(new_tag_list) > 5:
            error_message = "Too many tags. Maximum is 5"
            raise HTTPException(status_code=400, detail=error_message)
        for tag in new_tag_list:
            stmt = select(Tag).filter_by(name=tag)
            result = await db.execute(stmt)
            check_tag = result.scalar_one_or_none()
            if not check_tag:
                db_tag = Tag(name=tag)
                db.add(db_tag)
            tag_names.append(tag)
    photo = Photo(description=description.rstrip(), image_path=image_path,
                  user=user)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    if tags[0].strip():
        for tag_name in new_tag_list:
            stmt = select(Tag).filter_by(name=tag_name)
            result = await db.execute(stmt)
            tag = result.scalar_one_or_none()
            photo_tag = PhotoTag(photo_id=photo.id, tag_id=tag.id)
            db.add(photo_tag)
        await db.commit()
    await db.refresh(photo)
    await db.refresh(user)
    return PhotoInfo(
        photo_id=photo.id,
        username=photo.user.username,
        description=photo.description,
        image_path=photo.image_path,
        tags=tag_names
    )


async def get_my_photos(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = (
        select(Photo, User.username, Tag.name)
        .offset(offset)
        .limit(limit)
        .filter(Photo.user == user)
        .join(User)
        .outerjoin(PhotoTag)
        .outerjoin(Tag)
        .options(selectinload(Photo.tags))
    )
    result = await db.execute(stmt)

    photos_with_info = []
    for row in result:
        photo, username, tag = row
        print(photo)
        print(photo.tags)
        tags = [t.name for t in photo.tags] if photo.tags else []
        photo_info = PhotoInfo(
            photo_id=photo.id,
            username=username,
            description=photo.description,
            image_path=photo.image_path,
            tags=tags
        )
        photos_with_info.append(photo_info)

    if photos_with_info:
        return photos_with_info
    return {"message": "You haven't uploaded any photos yet"}


async def get_all_photos(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = (
        select(Photo, User.username, Tag.name)
        .offset(offset)
        .limit(limit)
        .join(User)
        .outerjoin(PhotoTag)
        .outerjoin(Tag)
        .options(selectinload(Photo.tags))
    )
    result = await db.execute(stmt)

    photos_with_info = []
    for row in result:
        photo, username, tag = row
        print(photo)
        print(photo.tags)
        tags = [t.name for t in photo.tags] if photo.tags else []
        photo_info = PhotoInfo(
            photo_id=photo.id,
            username=username,
            description=photo.description,
            image_path=photo.image_path,
            tags=tags
        )
        photos_with_info.append(photo_info)

    if photos_with_info:
        return photos_with_info
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
        photo.description = description.rstrip()
        await db.commit()
        await db.refresh(photo)
    return photo


async def delete_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this photo"
            )
        await db.delete(photo)
        await db.commit()
        return {"message": f"Photo with ID {photo_id} deleted successfully"}
    return {'message': f'Photo with ID {photo_id} not found'}


async def get_photo(photo_id: int, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    a = photo.scalar_one_or_none()
    return a


async def transform_photo(photo_id: int, transform_type, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to transform this photo"
            )
    url = photo.image_path
    url = url.split('/')[-1]
    result, option = utils.cloudinary_url(url, effect=transform_type.value)
    photo.image_path = result
    await db.commit()
    await db.refresh(photo)
    return TransformResult(
        photo_id=photo.id,
        new_image_path=photo.image_path,
        description=photo.description,
        created_at=photo.created_at,
        updated_at=photo.updated_at
    )
