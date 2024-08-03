import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}/{os.getenv('DATABASE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
