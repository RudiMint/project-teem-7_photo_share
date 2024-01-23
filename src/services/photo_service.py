from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Photo
from sqlalchemy.future import select

async def get_photo_by_id(photo_id: int, db: AsyncSession):
    stmt = select(Photo).where(Photo.id == photo_id)
    result = await db.execute(stmt)
    
    return result.scalar_one()
