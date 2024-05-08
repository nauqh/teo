from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(
    "postgresql://teodb_user:AqwLadtRc2z0EKNkislPgkhU5aDVXz2D@dpg-co7ugg4f7o1s738mu4gg-a.singapore-postgres.render.com/teodb")

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
