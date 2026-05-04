import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/database/accident_prediction.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False