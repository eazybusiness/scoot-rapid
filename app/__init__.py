"""
ScootRapid - Flask Application Factory
Microservice E-Scooter Rental Platform
"""

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from peewee import *
from playhouse.pool import PooledMySQLDatabase
import config

# Initialize extensions
login_manager = LoginManager()
mail = Mail()

# Global database reference
db = None

def init_database(app_config):
    """Initialize database connection"""
    global db
    
    db_config = app_config.DATABASE
    
    if db_config['engine'] == 'peewee.MySQLDatabase':
        db = PooledMySQLDatabase(
            db_config['name'],
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            charset=db_config['charset'],
            max_connections=10,
            stale_timeout=300
        )
    elif db_config['engine'] == 'peewee.SqliteDatabase':
        db = SqliteDatabase(db_config['name'])
    else:
        raise ValueError(f"Unsupported database engine: {db_config['engine']}")
    
    return db

def create_app(config_name):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config.config[config_name])
    
    # Initialize database
    database = init_database(app.config)
    
    # Initialize extensions
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Make database available to app
    app.database = database
    
    # Register blueprints
    from app.controllers import auth_bp, main_bp, scooter_bp, rental_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(scooter_bp)
    app.register_blueprint(rental_bp)
    
    # Register API blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Database connection management
    @app.before_request
    def before_request():
        database.connect()
    
    @app.teardown_request
    def teardown_request(exception):
        if not database.is_closed():
            database.close()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if not database.is_closed():
            database.close()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        from app.models import User, Scooter, Rental, Payment
        
        database.create_tables([User, Scooter, Rental, Payment], safe=True)
        print('Database initialized.')
    
    @app.cli.command()
    def create_admin():
        """Create an admin user"""
        from app.models import User
        
        email = input('Enter admin email: ')
        password = input('Enter admin password: ')
        
        try:
            admin = User.create_admin(
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            print(f'Admin user {email} created successfully.')
        except Exception as e:
            print(f'Failed to create admin user: {e}')
    
    return app
