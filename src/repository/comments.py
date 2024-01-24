from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, Depends
from sqlalchemy import select, delete

from src.database.models import Comment, User, Photo
from src.schemas.comments import CommentCreate, Comment as CommentResponse
from src.services.auth import auth_service
from src.services.photo_service import get_photo_by_id
from src.database.db import get_db

async def create_comment(photo_id: int, comment_data: CommentCreate, db: AsyncSession, user: User):
    """
    Create a new comment.

    :param photo_id: int: The ID of the photo for which the comment is being created.
    :param comment_data: CommentCreate: The details of the comment to be created.
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: CommentResponse: Details of the created comment.
    :raises HTTPException 404: If the associated photo is not found.
    :raises HTTPException 500: If an internal server error occurs.
    """
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
        return comment

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def get_comments(photo_id: int, limit: int, db: AsyncSession, user: User):
    """
    Get comments for a specific photo.

    :param photo_id: int: The ID of the photo for which comments are retrieved.
    :param limit: int: The maximum number of comments to retrieve (default 10).
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: List[CommentResponse]: List of comments for the specified photo.
    :raises HTTPException 404: If the associated photo is not found.
    """
    photo = await get_photo_by_id(photo_id, db)
    comments = await db.execute(select(Comment).filter(Comment.photo_id == photo.id).limit(limit).options(joinedload(Comment.user)))
    return comments.scalars().all()

async def edit_comment(comment_id: int, comment_data: CommentCreate, db: AsyncSession, user: User):
    """
    Update an existing comment.

    :param comment_id: int: The ID of the comment to be updated.
    :param comment_data: CommentCreate: The updated details of the comment.
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: CommentResponse: Details of the updated comment.
    :raises HTTPException 404: If the specified comment is not found.
    :raises HTTPException 500: If an internal server error occurs.
    """
    try:
        stmt_comment = select(Comment).filter_by(id=comment_id)
        comment = await db.execute(stmt_comment)
        comment_db = comment.scalar_one_or_none()

        if not comment_db:
            raise HTTPException(status_code=404, detail=f"Comment with id {comment_id} not found")

        for key, value in comment_data.dict().items():
            setattr(comment_db, key, value)
        comment_db.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(comment_db)

        return comment_db

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def delete_comment(comment_id: int, db: AsyncSession, user: User):
    """
    Delete an existing comment.

    :param comment_id: int: The ID of the comment to be deleted.
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: CommentResponse: Details of the deleted comment.
    :raises HTTPException 404: If the specified comment is not found.
    :raises HTTPException 500: If an internal server error occurs.
    """
    comment_result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment_model = comment_result.scalar()

    if not comment_model:
        return None

    if not user.is_admin and not user.is_moderator and comment_model.user_id != user.id:
        return None

    photo_id = comment_model.photo_id

    await db.execute(delete(Comment).where(Comment.id == comment_id))
    await db.commit()

    return CommentResponse(
        id=comment_model.id,
        text=comment_model.text,
        user_id=comment_model.user_id,
        created_at=comment_model.created_at,
        updated_at=comment_model.updated_at,
        photo_id=photo_id
    )
