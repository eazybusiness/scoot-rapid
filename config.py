import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration for MySQL with SQLAlchemy
    DB_NAME = os.environ.get('DB_NAME') or 'railway'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'INeEpewDMEAZLhrFlBrMkpPDTamfdqXb'
    DB_HOST = os.environ.get('DB_HOST') or 'mysql.railway.internal'
    DB_PORT = os.environ.get('DB_PORT') or '3306'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
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
    # Force Railway MySQL for all environments
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:INeEpewDMEAZLhrFlBrMkpPDTamfdqXb@mysql.railway.internal:3306/railway'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    # Force Railway MySQL for all environments
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:INeEpewDMEAZLhrFlBrMkpPDTamfdqXb@mysql.railway.internal:3306/railway'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': ProductionConfig  # Force production config to ensure MySQL
}
