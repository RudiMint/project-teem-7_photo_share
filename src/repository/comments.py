from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from src.database.models import Comment, User, Photo
from src.schemas.comments import CommentCreate, Comment as CommentResponse
from src.services.auth import auth_service
from src.services.photo_service import get_photo_by_id
from sqlalchemy.future import select

async def create_comment(photo_id: int, comment_data: CommentCreate, db: AsyncSession, user: User):
    stmt = select(Photo).filter_by(id=photo_id)
    photo = await db.execute(stmt)
    photo_db = photo.scalar_one_or_none()

    if not photo_db:
        raise HTTPException(status_code=404, detail=f"Photo with id {photo_id} not found")

    current_time = datetime.utcnow()
    comment = Comment(**comment_data.dict(), user_id=user.id, photo_id=photo_id, created_at=current_time)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    stmt = (
        select(Photo, User.username, Comment)
        .filter(Photo.id == photo_id)
        .join(User)
        .outerjoin(Comment, Comment.photo_id == Photo.id)
        .options(selectinload(Photo.tags), selectinload(Photo.comments))
    )
    result = await db.execute(stmt)
    row = result.fetchone()
    loaded_photo = row[0]

    return CommentResponse(
        photo_id=loaded_photo.id,
        username=loaded_photo.user.username,
        description=loaded_photo.description,
        image_path=loaded_photo.image_path,
        tags=[tag.name for tag in loaded_photo.tags] if loaded_photo.tags else [],
        comments=[CommentResponse(id=comment.id, text=comment.text, user_id=comment.user_id,
                                  created_at=comment.created_at) for comment in loaded_photo.comments] if loaded_photo.comments else []
    )

async def get_comments(photo_id: int, limit: int, db: AsyncSession, user: User):
    photo = await get_photo_by_id(photo_id, db)
    comments = await db.execute(select(Comment).filter(Comment.photo_id == photo.id).limit(limit))
    return comments.scalars().all()

async def edit_comment(comment_id: int, comment_data: CommentCreate, db: AsyncSession, user: auth_service.get_current_user):
    comment = await db.execute(select(Comment).filter_by(id=comment_id, user_id=user.id))
    if comment:
        comment = comment.scalar()
        if comment.user_id == user.id:
            for key, value in comment_data.dict().items():
                setattr(comment, key, value)
            comment.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(comment)
            return comment
    return None

async def delete_comment(comment_id: int, db: AsyncSession, user: User):
    comment = await db.execute(select(Comment).filter_by(id=comment_id))

    if not comment.scalar():
        return None

    comment_model = comment.scalar()

    if not user.is_admin and not user.is_moderator and comment_model.user_id != user.id:
        return None

    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()

    return comment_model
