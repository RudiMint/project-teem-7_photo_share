import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KEY, api_secret=config.CLD_API_SECRET, secure=True)


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"Web16/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user


async def check_db_connection(db: AsyncSession):
    try:
        # Execute a simple query to check the connection
        result = await db.execute(select(1))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

@router.get("/check_db", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_db_status(db: AsyncSession = Depends(get_db)):
    if await check_db_connection(db):
        return JSONResponse(content={"message": "Database is reachable"}, status_code=200)
    else:
        return JSONResponse(content={"message": "Failed to connect to the database"}, status_code=500)

@router.get("/", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")
    users = await repositories_users.get_all_users(db)
    return users


@router.post("/assign-moderator-role/{user_id}", response_model=UserResponse)
async def assign_moderator_role(user_id: int, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await repositories_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = Role.moderator
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/remove-moderator-role/{user_id}", response_model=UserResponse)
async def remove_moderator_role(user_id: int, db: AsyncSession = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    user = await repositories_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = Role.user
    await db.commit()
    await db.refresh(user)
    return user


@router.put("/set_admin_role", response_model=dict)
async def set_admin_role(email: str, db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(email, db)
    if user:
        user.role = Role.admin
        await db.commit()
        await db.refresh(user)
        return {"message": f"User with email {email} now has admin role"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
