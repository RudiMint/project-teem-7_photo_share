from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, Depends

from src.database.models import Comment, User, Photo
from src.schemas.comments import CommentCreate, Comment as CommentResponse
from src.services.auth import auth_service
from src.services.photo_service import get_photo_by_id
from src.database.db import get_db

async def create_comment(photo_id: int, comment_data: CommentCreate, db: AsyncSession, user: User):
    try:
        stmt_photo = select(Photo).filter_by(id=photo_id)
        photo = await db.execute(stmt_photo)
        photo_db = photo.scalar_one_or_none()

        if not photo_db:
            raise HTTPException(status_code=404, detail=f"Photo with id {photo_id} not found")

        current_time = datetime.utcnow()
        comment = Comment(**comment_data.dict(), user_id=user.id, photo_id=photo_id, created_at=current_time)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        await db.refresh(photo_db)

        return {"comment_id": comment.id, "photo_id": photo_db.id}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_comments(photo_id: int, limit: int, db: AsyncSession, user: User):
    photo = await get_photo_by_id(photo_id, db)
    comments = await db.execute(select(Comment).filter(Comment.photo_id == photo.id).limit(limit).options(joinedload(Comment.user)))
    return comments.scalars().all()

async def edit_comment(comment_id: int, comment_data: CommentCreate, db: AsyncSession, user: User):
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id))
    
    if comment.scalar():
        comment = comment.scalar()
        for key, value in comment_data.dict().items():
            setattr(comment, key, value)
        comment.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(comment)
        return CommentResponse(
            id=comment.id,
            text=comment.text,
            user_id=comment.user_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
    return None

async def delete_comment(comment_id: int, db: AsyncSession, user: User):
    comment = await db.execute(select(Comment).filter(Comment.id == comment_id))

    if not comment.scalar():
        return None

    comment_model = comment.scalar()

    if not user.is_admin and not user.is_moderator and comment_model.user_id != user.id:
        return None

    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()

    return CommentResponse(
        id=comment_model.id,
        text=comment_model.text,
        user_id=comment_model.user_id,
        created_at=comment_model.created_at,
        updated_at=comment_model.updated_at
    )
