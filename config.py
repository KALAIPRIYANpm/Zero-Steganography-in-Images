"""
Configuration file for DNA Image Cryptography Application
SQLite version
"""

import os

class Config:
    """Base configuration"""

    # Flask Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dna-image-crypto-secret-key-2026'

    # SQLite Database Configuration
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dna_image_crypto.db')

    # Flask Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

    # Email Configuration (for sending keys)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'

    # Admin Configuration
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD_HASH = 'pbkdf2:sha256:260000$salt$hash'  # Change in production


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}