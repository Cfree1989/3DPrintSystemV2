# app/__init__.py
from flask import Flask
from . import config # Import the config module from the current package
from . import extensions # Import extensions from the current package
from .models import job # Import models, specifically Job to ensure it's known by SQLAlchemy via extensions.db

def create_app(config_class_name="default"):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config.config[config_class_name])
    config.config[config_class_name].init_app(app)

    # Initialize extensions
    extensions.db.init_app(app)
    extensions.mail.init_app(app)
    extensions.migrate.init_app(app, extensions.db)

    # Register blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.dashboard import dashboard as dashboard_blueprint
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')

    # print("App created successfully with blueprints and extensions.") # Debug
    return app 