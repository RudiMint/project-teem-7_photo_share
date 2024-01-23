from typing import List

import cloudinary
from cloudinary import uploader
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.db import get_db
from src.database.models import User, TransformationType
from src.schemas.photo import PhotoResponse, PhotoInfo
from src.services.auth import auth_service
from src.repository import photo as repositories_photos
from src.conf.config import config

router = APIRouter(prefix='/photos', tags=['photos'])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET
)


@router.post("/", response_model=PhotoInfo, status_code=status.HTTP_201_CREATED)
async def upload_photo(file: UploadFile = File(...),
                       description: str = Form(...),
                       tags: List[str] = Form(None), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    unique_id = int(datetime.now().timestamp())
    public_id = f"goitgroup7_{user.email}_{unique_id}"
    try:
        cloudinary_result = cloudinary.uploader.upload(file.file,
                                                       public_id=public_id)
        cloudinary_result = cloudinary_result.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    photo = await repositories_photos.create_photo_info(description, tags, db, user, cloudinary_result)
    return photo


@router.get("/{user.id}/all", response_model=list[PhotoInfo])
async def get_my_photos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photos = await repositories_photos.get_my_photos(limit, offset, db, user)
    return photos


@router.get("/all", response_model=list[PhotoInfo])
async def get_all_photos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                         db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photos = await repositories_photos.get_all_photos(limit, offset, db, user)
    return photos


@router.put("/transform/{photo_id}")
async def transform_photo(photo_id: int, transform_type: TransformationType, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):
    transform_result = await repositories_photos.transform_photo(photo_id, transform_type, db, user)
    # return {'message': 'goood'}
    return transform_result


@router.get("/{photo_id}", response_model=PhotoResponse)  # response_model=PhotoWithTagsSchema
async def get_photo(photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):
    todo = await repositories_photos.get_photo(photo_id, db, user)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return todo


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(description: str = Form(...), photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    photo = await repositories_photos.update_photo(photo_id, description, db, user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return photo


@router.delete("/{photo_id}")  # status_code=status.HTTP_204_NO_CONTENT
async def delete_photo(photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    todo = await repositories_photos.delete_photo(photo_id, db, user)
    return todo
