# Initialize Flask extensions (e.g., db, migrate) here
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
def init_extensions(app):
    """Initialize Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Add any other extensions here
    # e.g., login_manager.init_app(app)
    
    return app