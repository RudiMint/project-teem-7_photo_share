from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.database.db import get_db
from src.database.models import User
from src.schemas.comments import CommentCreate, Comment as CommentResponse
from src.services.auth import auth_service
from src.repository import comments as comment_repository

router = APIRouter(prefix='/comments', tags=['comments'])

@router.post("/", response_model=CommentResponse)
async def create_comment(photo_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Create a new comment.

    :param photo_id: int: The ID of the photo for which the comment is being created.
    :param comment: CommentCreate: The details of the comment to be created.
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: CommentResponse: Details of the created comment.
    :raises HTTPException 404: If the associated photo is not found.
    :raises HTTPException 500: If an internal server error occurs.
    """
    return await comment_repository.create_comment(photo_id, comment, db, user)

@router.get("/{photo_id}", response_model=List[CommentResponse])
async def get_comments(photo_id: int, limit: int = Query(10, ge=1, le=100),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
    Get comments for a specific photo.

    :param photo_id: int: The ID of the photo for which comments are retrieved.
    :param limit: int: The maximum number of comments to retrieve (default 10).
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: List[CommentResponse]: List of comments for the specified photo.
    :raises HTTPException 404: If the associated photo is not found.
    """
    comments = await comment_repository.get_comments(photo_id, limit, db, user)
    return comments

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, comment_data: CommentCreate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
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
    comment = await comment_repository.edit_comment(comment_id, comment_data, db, user)
    return comment

@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Delete an existing comment.

    :param comment_id: int: The ID of the comment to be deleted.
    :param db: AsyncSession: Database session dependency.
    :param user: User: Current authenticated user dependency.
    :return: CommentResponse: Details of the deleted comment.
    :raises HTTPException 404: If the specified comment is not found.
    :raises HTTPException 500: If an internal server error occurs.
    """
    comment = await comment_repository.delete_comment(comment_id, db, user)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")

    return comment
