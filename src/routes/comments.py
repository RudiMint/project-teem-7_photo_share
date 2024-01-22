from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.comments import CommentCreate, Comment as CommentResponse
from src.services.auth import auth_service
from src.repository import comments as comment_repository

router = APIRouter(prefix='/comments', tags=['comments'])


@router.post("/", response_model=CommentResponse)
async def create_comment(photo_id: int, comment: CommentCreate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    comment = await comment_repository.create_comment(photo_id, comment, db, user)
    return comment


@router.get("/{photo_id}", response_model=list[CommentResponse])
async def get_comments(photo_id: int, limit: int = Query(10, ge=1, le=100),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    comments = await comment_repository.get_comments(photo_id, limit, db, user)
    return comments


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, new_content: str, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    comment = await comment_repository.update_comment(comment_id, new_content, db, user)
    return comment

@router.delete("/{comment_id}", response_model=CommentResponse)
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    comment = await comment_repository.delete_comment(comment_id, db, user)

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found or permission denied")

    return comment
