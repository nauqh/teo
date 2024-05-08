from sqlalchemy import (create_engine, Column, ForeignKey,
                        DateTime, String, Integer, BigInteger, Boolean)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from ast import literal_eval
import pandas as pd

from bot.utils.log import get_logger

log = get_logger(__name__)

# engine = create_engine(
#     "postgresql://teodb_user:AqwLadtRc2z0EKNkislPgkhU5aDVXz2D@dpg-co7ugg4f7o1s738mu4gg-a.singapore-postgres.render.com/teodb")
engine = create_engine("sqlite:///teo.db")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    is_bot = Column(Boolean)
    roles = relationship("Role", secondary="user_role", back_populates="users")

    threads = relationship("Thread")

    def __repr__(self) -> str:
        return f"<User(name={self.name}, is_bot={self.is_bot})>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    position = Column(Integer, nullable=False)
    users = relationship("User", secondary="user_role", back_populates="roles")

    def __repr__(self) -> str:
        return f"<Role(name={self.name}, position={self.position})>"


class Thread(Base):
    __tablename__ = "threads"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    tags = Column(String, nullable=False)
    messages = Column(String, nullable=False)

    author_id = Column(ForeignKey("users.id"))
    author = relationship("User", back_populates="threads")


class Message(Base):
    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)


if __name__ == "__main__":
    Base.metadata.drop_all(engine, tables=[Base.metadata.tables["user_role"],
                                           Base.metadata.tables["users"],
                                           Base.metadata.tables["roles"],
                                           Base.metadata.tables["threads"],
                                           Base.metadata.tables["tags"]])

    log.info("Initialize database connection")
    Base.metadata.create_all(bind=engine)

    threaddf = pd.read_csv("data/threads.csv",
                           parse_dates=['created_at'], converters={'tags': literal_eval,
                                                                   'messages': literal_eval})

    userdf = pd.read_csv("data/users.csv",
                         converters={'roles': literal_eval})
    roledf = pd.read_csv("data/roles.csv")

    log.info("Add users and roles")
    with Session() as session:
        users = []
        roles = []
        for _, row in userdf.iterrows():
            user = User(id=row['id'], name=row['name'], is_bot=row['is_bot'])
            users.append(user)
        for _, row in roledf.iterrows():
            role = Role(id=row['id'], name=row['name'],
                        position=row['position'])
            roles.append(role)

        session.add_all(users)
        session.add_all(roles)
        session.commit()

        # Add associations
        user_dict = {user.id: user for user in session.query(User).all()}
        role_dict = {role.id: role for role in session.query(Role).all()}

        df = userdf[['id', 'roles']]
        associations = df.explode('roles').reset_index(drop=True).rename(
            columns={'roles': 'role'}).to_dict(orient='records')

        for ass in associations:
            user = user_dict.get(ass["id"])
            role = role_dict.get(ass["role"])
            if user and role:
                user.roles.append(role)

        session.commit()

    log.info("Add threads")
    with Session() as session:
        threads = []
        for _, row in threaddf.iterrows():
            thread = Thread(id=row['id'],
                            name=row['name'], created_at=row['created_at'],
                            tags=str(row['tags']),
                            messages=str([message['id']
                                          for message in row['messages']]),
                            author_id=row['author_id'])
            threads.append(thread)
        session.add_all(threads)
        session.commit()

    log.info("Add tags")
    tagdf = pd.read_csv("data/tags.csv")
    with Session() as session:
        tags = []
        for _, row in tagdf.iterrows():
            tag = Tag(id=row['id'], name=row['name'])
            tags.append(tag)
        session.add_all(tags)
        session.commit()
