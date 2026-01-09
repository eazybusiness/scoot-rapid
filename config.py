import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration for MySQL with SQLAlchemy
    DB_NAME = os.environ.get('DB_NAME') or 'scoot_rapid'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Pricing configuration
    BASE_PRICE_PER_MINUTE = float(os.environ.get('BASE_PRICE_PER_MINUTE') or 0.30)
    START_FEE = float(os.environ.get('START_FEE') or 1.50)
    
    # Application settings
    MAX_RENTAL_TIME_HOURS = int(os.environ.get('MAX_RENTAL_TIME_HOURS') or 12)
    QR_CODE_EXPIRY_MINUTES = int(os.environ.get('QR_CODE_EXPIRY_MINUTES') or 10)

class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = os.environ.get('DEV_DB_NAME') or 'scoot_rapid_dev'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}?charset=utf8mb4"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    DB_NAME = os.environ.get('PROD_DB_NAME') or 'scoot_rapid_prod'
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{DB_NAME}?charset=utf8mb4"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
