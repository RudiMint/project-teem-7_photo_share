from typing import List

import cloudinary
from cloudinary import uploader
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.photo import PhotoResponse, PhotoSchema
from src.services.auth import auth_service
from src.repository import photo as repositories_photos
from src.conf.config import config as config_connect

router = APIRouter(prefix='/photos', tags=['photos'])

cloudinary.config(
    cloud_name=config_connect.CLD_NAME,
    api_key=config_connect.CLD_API_KEY,
    api_secret=config_connect.CLD_API_KEY
)


@router.post("/", status_code=status.HTTP_201_CREATED)  # response_model=PhotoResponse
async def upload_photo(file: UploadFile = File(...),
                       description: str = Form(...),
                       tags: List[str] = Form(None), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    try:
        cloudinary_result = cloudinary.uploader.upload(file.file,
                                                       public_id="goitgroup7")
        cloudinary_result = cloudinary_result.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    todo = await repositories_photos.create_photo_info(description, tags, db, user, cloudinary_result)
    return todo


@router.get("/all", response_model=list[PhotoResponse])  # response_model=list[PhotoResponse]
async def get_all_todos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photos = await repositories_photos.get_all_photos(limit, offset, db, user)
    return photos