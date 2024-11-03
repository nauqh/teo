from sqlalchemy import Column, BIGINT, String, DateTime, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

engine = create_engine(
    "DB_CONNECTION_STRING"
)

# Association tables
thread_tag_table = Table(
    'thread_tag', Base.metadata,
    Column('thread_id', BIGINT, ForeignKey('threads.id'), primary_key=True),
    Column('tag_id', BIGINT, ForeignKey('tags.id'), primary_key=True)
)

user_role_table = Table(
    'user_role', Base.metadata,
    Column('user_id', BIGINT, ForeignKey('users.id'), primary_key=True),
    Column('role_id', BIGINT, ForeignKey('roles.id'), primary_key=True)
)

# Models


class Thread(Base):
    __tablename__ = 'threads'

    id = Column(BIGINT, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    user_id = Column(BIGINT, ForeignKey('users.id'), nullable=True)
    response_msg_id = Column(BIGINT, nullable=True)

    messages = relationship("Message", back_populates="thread")
    tags = relationship("Tag", secondary=thread_tag_table,
                        back_populates="threads")


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(BIGINT, primary_key=True)
    name = Column(String, nullable=False)

    threads = relationship(
        "Thread", secondary=thread_tag_table, back_populates="tags")


class Message(Base):
    __tablename__ = 'messages'

    id = Column(BIGINT, primary_key=True)
    content = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    user_id = Column(BIGINT, ForeignKey('users.id'), nullable=False)
    thread_id = Column(BIGINT, ForeignKey('threads.id'), nullable=False)

    thread = relationship("Thread", back_populates="messages")


class User(Base):
    __tablename__ = 'users'

    id = Column(BIGINT, primary_key=True)
    name = Column(String, nullable=False)

    roles = relationship("Role", secondary=user_role_table,
                         back_populates="users")


class Role(Base):
    __tablename__ = 'roles'

    id = Column(BIGINT, primary_key=True)
    name = Column(String, nullable=False)

    users = relationship("User", secondary=user_role_table,
                         back_populates="roles")


# Create tables
Base.metadata.create_all(engine)
