import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration for MySQL with Peewee
    DATABASE = {
        'engine': 'peewee.MySQLDatabase',
        'name': os.environ.get('DB_NAME') or 'scoot_rapid',
        'user': os.environ.get('DB_USER') or 'root',
        'password': os.environ.get('DB_PASSWORD') or '',
        'host': os.environ.get('DB_HOST') or 'localhost',
        'port': int(os.environ.get('DB_PORT') or 3306),
        'charset': 'utf8mb4'
    }
    
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
    DATABASE = Config.DATABASE.copy()
    DATABASE['name'] = os.environ.get('DEV_DB_NAME') or 'scoot_rapid_dev'

class TestingConfig(Config):
    TESTING = True
    DATABASE = {
        'engine': 'peewee.SqliteDatabase',
        'name': ':memory:'
    }
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    DATABASE = Config.DATABASE.copy()
    DATABASE['name'] = os.environ.get('PROD_DB_NAME') or 'scoot_rapid_prod'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
