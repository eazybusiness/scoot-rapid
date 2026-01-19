"""
ScootRapid - Flask Application Factory
Lean E-Scooter Rental Platform
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
jwt = JWTManager()

def create_app(config_name=None):
    """Application factory pattern"""
    from config import config
    
    # Use environment variable or default to production
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Debug: Log which config is being used
    app.logger.info(f"Using config: {config_name}")
    app.logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.controllers import auth_bp, main_bp, scooter_bp, rental_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(scooter_bp)
    app.register_blueprint(rental_bp)
    
    # Register API blueprints
    from app.controllers.api_controller import api_bp
    app.register_blueprint(api_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        return {'error': 'Unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden'}, 403
    
    # Initialize database tables on startup
    with app.app_context():
        try:
            # Debug: Log which database URL is being used
            app.logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            # Ignore duplicate table and ENUM type errors (happens on redeploy)
            if "already exists" not in str(e) and "duplicate key value violates unique constraint" not in str(e):
                app.logger.error(f"Database initialization error: {e}")
            else:
                app.logger.info("Database tables already exist - skipping creation")
    
    # CLI commands
    @app.cli.command()
    def init_db():
        """Initialize the database"""
        db.create_all()
        print('Database initialized.')
    
    @app.cli.command()
    def create_admin():
        """Create an admin user"""
        from app.models.user import User
        
        email = input('Enter admin email: ')
        password = input('Enter admin password: ')
        first_name = input('Enter first name: ')
        last_name = input('Enter last name: ')
        
        try:
            admin = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f'Admin user {email} created successfully.')
        except Exception as e:
            db.session.rollback()
            print(f'Failed to create admin user: {e}')
    
    return app
