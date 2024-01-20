from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.models import Comment
from src.schemas.comments import CommentCreate
from src.services.auth import auth_service
from src.services.photo_service import get_photo_by_id

async def create_comment(photo_id: int, comment_data: CommentCreate, db: AsyncSession, user: auth_service.get_current_user):
    photo = await get_photo_by_id(photo_id, db)
    if photo:
        comment = Comment(**comment_data.dict(), user_id=user.id, photo_id=photo.id)
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    return None

async def get_comments(photo_id: int, limit: int, db: AsyncSession, user: auth_service.get_current_user):
    photo = await get_photo_by_id(photo_id, db)
    if photo:
        comments = await db.execute(select(Comment).filter_by(photo_id=photo.id).limit(limit))
        return comments.scalars().all()
    return []

async def edit_comment(comment_id: int, comment_data: CommentCreate, db: AsyncSession, user: auth_service.get_current_user):
    comment = await db.execute(select(Comment).filter_by(id=comment_id, user_id=user.id))
    if comment:
        comment = comment.scalar()
        if comment.user_id == user.id:
            for key, value in comment_data.dict().items():
                setattr(comment, key, value)
            await db.commit()
            return comment
    return None
