import os
import secrets

class Config:
    # Try to get from environment, otherwise generate a secure random key for dev
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///surplus2serve.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = "None"
    SESSION_COOKIE_SECURE = True


