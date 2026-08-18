import os
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change_me')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(basedir / 'uploads'))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f"sqlite:///{basedir / 'pacientes.db'}"
    )

class ProdConfig(Config):
    DEBUG = False

class DevConfig(Config):
    DEBUG = True
