from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Photo

async def get_photo_by_id(photo_id: int, db: AsyncSession):
    photo = await db.execute(
        Photo.select().where(Photo.id == photo_id)
    )
    
    return photo.scalar()
