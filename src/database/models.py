import enum
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Enum, Column, Boolean


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column("updated_at", DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column("role", Enum(Role), default=Role.user, nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)


class Image(Base):
    __tablename__ = "images"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    tags: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("images.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    image_path: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String(255))
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)


class PhotoTag(Base):
    __tablename__ = "photo_tags"

    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

Photo.tags = relationship("Tag", secondary="photo_tags", back_populates="photos")
Tag.photos = relationship("Photo", secondary="photo_tags", back_populates="tags")
User.photos = relationship("Photo", back_populates="user")
Photo.user = relationship("User", back_populates="photos")

User.images = relationship("Image", back_populates="user")
User.comments = relationship("Comment", back_populates="user")
Image.user = relationship("User", back_populates="images")
Image.comments = relationship("Comment", back_populates="image")
Comment.user = relationship("User", back_populates="comments")
Comment.image = relationship("Image", back_populates="comments")
