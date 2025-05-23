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

    # Register template filters for display formatting
    from .utils.helpers import (
        get_printer_display_name, get_color_display_name, get_discipline_display_name,
        format_datetime_local, format_datetime_detailed, round_time_conservative
    )
    app.jinja_env.filters['printer_name'] = get_printer_display_name
    app.jinja_env.filters['color_name'] = get_color_display_name
    app.jinja_env.filters['discipline_name'] = get_discipline_display_name
    app.jinja_env.filters['local_datetime'] = format_datetime_local
    app.jinja_env.filters['detailed_datetime'] = format_datetime_detailed
    app.jinja_env.filters['round_time'] = round_time_conservative

    return app 