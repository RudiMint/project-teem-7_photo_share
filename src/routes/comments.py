from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.schemas.comments import Comment, CommentCreate
from src.database.db import get_db
from typing import List

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/photos/{photo_id}/", response_model=Comment)
async def create_comment(
    photo_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db)
):
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    new_comment = Comment(**comment.dict(), photo_id=photo_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/photos/{photo_id}/", response_model=List[Comment])
async def get_comments_for_photo(photo_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.photo_id == photo_id).all()
    return comments