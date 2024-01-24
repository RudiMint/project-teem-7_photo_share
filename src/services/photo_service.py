from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Photo
from sqlalchemy.future import select

async def get_photo_by_id(photo_id: int, db: AsyncSession):
    """
    Retrieve a photo from the database based on its ID.

    :param photo_id: int: The ID of the photo to retrieve.
    :param db: AsyncSession: The asynchronous database session.

    :return: Photo: The retrieved photo.
    """
    stmt = select(Photo).where(Photo.id == photo_id)
    result = await db.execute(stmt)
    
    return result.scalar_one()
