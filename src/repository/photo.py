from cloudinary import utils
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from src.database.models import Photo, User, Tag, PhotoTag
from src.schemas.photo import PhotoInfo, TransformResult


async def create_photo_info(description: str, tags, db: AsyncSession, user: User, image_path):

    """
    The create_photo_info function takes in a description, tags, db session, user object and image path.
    It then creates a new photo object with the given information and adds it to the database.
    If there are any new tags that need to be created they will be added as well.
    The function returns a PhotoInfo object containing all of the information about the newly created photo.

    :param description: str: Pass the description of the photo
    :param tags: Get the tags from the request body
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the username of the user who uploaded
    :param image_path: Save the image to the server
    :return: A photoinfo object
    :doc-author: Trelent
    """
    new_tag_list = None
    tag_names = []
    if tags[0].strip():
        new_tag_list = tags[0].split(',')
        if len(new_tag_list) > 5:
            error_message = "Too many tags. Maximum is 5"
            raise HTTPException(status_code=400, detail=error_message)
        for tag in new_tag_list:
            stmt = select(Tag).filter_by(name=tag)
            result = await db.execute(stmt)
            check_tag = result.scalar_one_or_none()
            if not check_tag:
                db_tag = Tag(name=tag)
                db.add(db_tag)
            tag_names.append(tag)
    photo = Photo(description=description.rstrip(), image_path=image_path,
                  user=user)
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    if tags[0].strip():
        for tag_name in new_tag_list:
            stmt = select(Tag).filter_by(name=tag_name)
            result = await db.execute(stmt)
            tag = result.scalar_one_or_none()
            photo_tag = PhotoTag(photo_id=photo.id, tag_id=tag.id)
            db.add(photo_tag)
        await db.commit()
    await db.refresh(photo)
    await db.refresh(user)
    return PhotoInfo(
        photo_id=photo.id,
        username=photo.user.username,
        description=photo.description,
        image_path=photo.image_path,
        tags=tag_names
    )


async def get_my_photos(limit: int, offset: int, db: AsyncSession, user: User):

    """
    The get_my_photos function returns a list of PhotoInfo objects, which contain the following information:
        - photo_id: The id of the photo in question.
        - username: The username of the user who uploaded this photo.
        - description: A short description that accompanies this image.
        - image_path: The path to where this image is stored on our server (this will be used by frontend).

    :param limit: int: Limit the number of photos returned
    :param offset: int: Specify the number of photos to skip before returning results
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the photos by user
    :return: A list of photoinfo objects
    :doc-author: Trelent
    """
    stmt = (
        select(Photo, User.username, Tag.name)
        .distinct(Photo.id)
        .offset(offset)
        .limit(limit)
        .filter(Photo.user == user)
        .join(User)
        .outerjoin(PhotoTag)
        .outerjoin(Tag)
        .options(selectinload(Photo.tags))
    )
    result = await db.execute(stmt)

    photos_with_info = []
    for row in result:
        photo, username, tag = row
        tags = [t.name for t in photo.tags] if photo.tags else []
        photo_info = PhotoInfo(
            photo_id=photo.id,
            username=username,
            description=photo.description,
            image_path=photo.image_path,
            tags=tags
        )
        photos_with_info.append(photo_info)

    if photos_with_info:
        return photos_with_info
    return {"message": "You haven't uploaded any photos yet"}


async def get_all_photos(limit: int, offset: int, db: AsyncSession, user: User):

    """
    The get_all_photos function returns a list of all photos in the database.

    :param limit: int: Limit the number of photos returned
    :param offset: int: Skip the first n photos
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the username of the user who uploaded a photo
    :return: A list of photoinfo objects
    :doc-author: Trelent
    """
    stmt = (
        select(Photo, User.username, Tag.name)
        .distinct(Photo.id)
        .offset(offset)
        .limit(limit)
        .join(User)
        .outerjoin(PhotoTag)
        .outerjoin(Tag)
        .options(selectinload(Photo.tags))
    )
    result = await db.execute(stmt)

    photos_with_info = []
    for row in result:
        photo, username, tag = row
        print(photo)
        print(photo.tags)
        tags = [t.name for t in photo.tags] if photo.tags else []
        photo_info = PhotoInfo(
            photo_id=photo.id,
            username=username,
            description=photo.description,
            image_path=photo.image_path,
            tags=tags
        )
        photos_with_info.append(photo_info)

    if photos_with_info:
        return photos_with_info
    return {"message": "You haven't uploaded any photos yet"}


async def update_photo(photo_id: int, description, db: AsyncSession, user: User):

    """
    The update_photo function takes in a photo_id, description, db and user.
    It then creates a statement that selects the Photo table where the id is equal to
    the photo_id and user is equal to the user. It then executes this statement on db.
    The result of this execution is stored in result variable as an object of type ResultProxy.
    This object has a method called scalar_one_or_none() which returns one row or None if no rows are returned by query execution. This row (if it exists) is stored in photo variable as an object of type Photo class defined above using SQL

    :param photo_id: int: Identify the photo to be deleted
    :param description: Update the description of a photo
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Check if the user is the owner of the photo
    :return: The updated photo, or none if the photo does not exist
    :doc-author: Trelent
    """
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    result = await db.execute(stmt)
    photo = result.scalar_one_or_none()
    if photo:
        print(user.role.value)
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to edit this photo"
            )
        photo.description = description.rstrip()
        await db.commit()
        await db.refresh(photo)
    return photo


async def delete_photo(photo_id: int, db: AsyncSession, user: User):

    """
    The delete_photo function deletes a photo from the database.
        Args:
            photo_id (int): The ID of the photo to delete.
            db (AsyncSession): An async session for interacting with the database.
            user (User): The current user, used to check if they have permission to delete this photo.

    :param photo_id: int: Specify the id of the photo to be deleted
    :param db: AsyncSession: Pass in the database session to the function
    :param user: User: Get the user object from the database
    :return: A dictionary with a message that indicates whether the photo was deleted successfully or not
    :doc-author: Trelent
    """
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to delete this photo"
            )
        await db.delete(photo)
        await db.commit()
        return {"message": f"Photo with ID {photo_id} deleted successfully"}
    return {'message': f'Photo with ID {photo_id} not found'}


async def get_photo(photo_id: int, db: AsyncSession, user: User):

    """
    The get_photo function takes in a photo_id and returns the corresponding Photo object.
        Args:
            photo_id (int): The id of the Photo to be returned.
            db (AsyncSession): An async session for querying the database.
            user (User): The User who owns this photo, used to ensure that only photos belonging to this user are returned.

    :param photo_id: int: Specify the photo id of the photo that we want to get
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user is only able to access their own photos
    :return: A photo object
    :doc-author: Trelent
    """
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    a = photo.scalar_one_or_none()
    return a


async def transform_photo(photo_id: int, transform_type, db: AsyncSession, user: User):

    """
    The transform_photo function takes in a photo_id, transform_type and db.
    It then checks if the user has permission to transform the photo. If they do, it gets the url of
    the image from cloudinary and transforms it using utils.cloudinary_url(). It then updates the database with
    the new image path and returns a TransformResult object.

    :param photo_id: int: Identify the photo to be transformed
    :param transform_type: Determine which transformation to apply
    :param db: AsyncSession: Access the database
    :param user: User: Check if the user has permission to delete the photo
    :return: A transformresult object
    :doc-author: Trelent
    """
    stmt = select(Photo).filter_by(id=photo_id, user=user)
    photo = await db.execute(stmt)
    photo = photo.scalar_one_or_none()
    if photo:
        if photo.owner_id != user.id and user.role.value != "admin":
            raise HTTPException(
                status_code=403, detail="You don't have permission to transform this photo"
            )
    url = photo.image_path
    url = url.split('/')[-1]
    result, option = utils.cloudinary_url(url, effect=transform_type.value)
    photo.image_path = result
    await db.commit()
    await db.refresh(photo)
    return TransformResult(
        photo_id=photo.id,
        new_image_path=photo.image_path,
        description=photo.description,
        created_at=photo.created_at,
        updated_at=photo.updated_at
    )
