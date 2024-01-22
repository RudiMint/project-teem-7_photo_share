from typing import List

import cloudinary
from cloudinary import uploader
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.photo import PhotoResponse, PhotoSchema, PhotoUpdateSchema
from src.services.auth import auth_service
from src.repository import photo as repositories_photos

router = APIRouter(prefix='/photos', tags=['photos'])



@router.post("/", status_code=status.HTTP_201_CREATED)  # response_model=PhotoResponse
async def upload_photo(file: UploadFile = File(...),
                       description: str = Form(...),
                       tags: List[str] = Form(None), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):
    public_id = f"goitgroup7/{user.email}"
    try:
        cloudinary_result = cloudinary.uploader.upload(file.file,
                                                       public_id=public_id)
        cloudinary_result = cloudinary_result.get("url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    todo = await repositories_photos.create_photo_info(description, tags, db, user, cloudinary_result)
    return todo


@router.get("/all", response_model=list[PhotoResponse])
async def get_all_todos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    photos = await repositories_photos.get_all_photos(limit, offset, db, user)
    return photos


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_todo(photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                   user: User = Depends(auth_service.get_current_user)):
    todo = await repositories_photos.get_photo(photo_id, db, user)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return todo


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_todo(description: str = Form(...), photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    photo = await repositories_photos.update_photo(photo_id, description, db, user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return photo

@router.delete("/{photo_id}", response_model=dict)
async def delete_photo_endpoint(photo_id: int, db: AsyncSession = Depends(get_db),
                                user: User = Depends(auth_service.get_current_user)):
    result = await repositories_photos.delete_photo(photo_id, db, user)
    return result
