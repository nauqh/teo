from sqlalchemy import (Column, ForeignKey,
                        DateTime, ARRAY, String, Integer, BigInteger, Boolean)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    users = relationship("User", secondary="user_role", back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(name={self.name}, position={self.position})>"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    is_bot = Column(Boolean, nullable=False)
    roles = relationship("Role", secondary="user_role", back_populates="users")

    threads = relationship("Thread")

    def __repr__(self) -> str:
        return f"<User(name={self.name}, is_bot={self.is_bot})>"


class Thread(Base):
    __tablename__ = "threads"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    messages = Column(ARRAY(String), nullable=False)

    author_id = Column(ForeignKey("users.id"))
    author = relationship("User", back_populates="threads")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
