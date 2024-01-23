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

    """
    The upload_photo function is used to upload a photo to the database.
        The function takes in an UploadFile object, which contains the file that will be uploaded.
        It also takes in a description and tags for the photo, as well as a database session and user object.

    :param file: UploadFile: Get the file from the request
    :param description: str: Get the description of the photo from the request body
    :param tags: List[str]: Allow the user to add tags to their photo
    :param db: AsyncSession: Get a database connection
    :param user: User: Get the current user
    :return: A photo object
    :doc-author: Trelent
    """
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


@router.get("/{user.id}/all")  # response_model=list[PhotoInfo]
async def get_my_photos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                        db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    The get_my_photos function returns a list of photos that the user has uploaded.

    :param limit: int: Limit the number of photos returned
    :param ge: Specify the minimum value for the limit parameter
    :param le: Limit the maximum number of photos that can be returned
    :param offset: int: Specify the offset of the photos to be returned
    :param ge: Set a minimum value for the limit parameter
    :param db: AsyncSession: Get the database connection
    :param user: User: Get the current user from the auth_service
    :return: A list of photo objects
    :doc-author: Trelent
    """
    photos = await repositories_photos.get_my_photos(limit, offset, db, user)
    return photos


@router.get("/all")  # response_model=list[PhotoInfo]
async def get_all_photos(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                         db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):

    """
    The get_all_photos function returns a list of all photos in the database.

    :param limit: int: Limit the number of photos returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Limit the number of photos returned to 500
    :param offset: int: Specify the number of photos to skip
    :param ge: Set a minimum value for the limit parameter
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user, and then pass it to the repositories_photos
    :return: A list of photos
    :doc-author: Trelent
    """
    photos = await repositories_photos.get_all_photos(limit, offset, db, user)
    return photos


@router.put("/transform/{photo_id}")
async def transform_photo(photo_id: int, transform_type: TransformationType, db: AsyncSession = Depends(get_db),
                          user: User = Depends(auth_service.get_current_user)):

    """
    The transform_photo function takes a photo_id and a transform_type,
        then transforms the photo with the given transformation type.

    :param photo_id: int: Get the photo id from the url
    :param transform_type: TransformationType: Specify the type of transformation to be applied on the photo
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: A dictionary with two keys:
    :doc-author: Trelent
    """
    transform_result = await repositories_photos.transform_photo(photo_id, transform_type, db, user)
    return transform_result


@router.get("/{photo_id}", response_model=PhotoResponse)  # response_model=PhotoWithTagsSchema
async def get_photo(photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                    user: User = Depends(auth_service.get_current_user)):

    """
    The get_photo function returns a photo by its id.

    :param photo_id: int: Specify the id of the photo to be retrieved
    :param db: AsyncSession: Pass a database connection to the function
    :param user: User: Get the current user from the database
    :return: A photo object
    :doc-author: Trelent
    """
    todo = await repositories_photos.get_photo(photo_id, db, user)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return todo


@router.put("/{photo_id}", response_model=PhotoResponse)
async def update_photo(description: str = Form(...), photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):

    """
    The update_photo function updates the description of a photo.
        The function takes in an integer representing the id of a photo, and returns that same photo with its updated
        description. If no such photo exists, then it will return 404 NOT FOUND.

    :param description: str: Get the description of the photo from the request body
    :param photo_id: int: Get the photo id from the path
    :param db: AsyncSession: Get the database session
    :param user: User: Get the user from the token
    :return: The updated photo object (with the new description)
    :doc-author: Trelent
    """
    photo = await repositories_photos.update_photo(photo_id, description, db, user)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return photo


@router.delete("/{photo_id}")  # status_code=status.HTTP_204_NO_CONTENT
async def delete_photo(photo_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                       user: User = Depends(auth_service.get_current_user)):

    """
    The delete_photo function deletes a photo from the database.
        The function takes in an integer representing the id of the photo to be deleted,
        and returns a dictionary with information about whether or not it was successful.

    :param photo_id: int: Get the photo id from the url
    :param db: AsyncSession: Pass the database session to the repository layer
    :param user: User: Get the current user from the database
    :return: A dict with the following keys:
    :doc-author: Trelent
    """
    todo = await repositories_photos.delete_photo(photo_id, db, user)
    return todo
