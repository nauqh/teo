import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TOKEN = os.getenv("TOKEN")
    GUILD = int(os.getenv("GUILD"))
    ADMIN = int(os.getenv("ADMIN"))
    FORUM_CHANNEL = int(os.getenv("FORUM_CHANNEL"))
    EXAM_CHANNEL = int(os.getenv("EXAM_CHANNEL"))
    STAFF_CHANNEL = int(os.getenv("STAFF_CHANNEL"))
