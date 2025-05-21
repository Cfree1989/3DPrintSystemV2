# app/config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__)) # app directory
project_root = os.path.dirname(basedir) # Project root (3DPrintSystemV2)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    # Path to the main 'storage' directory as seen by the Flask application
    # For development, it's <project_root>/storage
    # For production, set APP_STORAGE_ROOT environment variable to the UNC path or direct path
    # e.g., '//SERVER/SHARE/3DPrintSystemV2/storage'
    APP_STORAGE_ROOT = os.environ.get('APP_STORAGE_ROOT') or os.path.join(project_root, 'storage')

    # Base path used in 3dprint:// URLs and validated by SlicerOpener.py
    # Staff machines must have this path correctly pointing to the shared 'storage' directory.
    # e.g., 'Z:\\3DPrintSystemV2\\storage' (Note: use double backslashes in Python strings or raw strings r'Z:\\3DPrintSystemV2\\storage')
    SLICER_PROTOCOL_BASE_PATH = os.environ.get('SLICER_PROTOCOL_BASE_PATH') or 'Z:\\3DPrintSystemV2\\storage' # Make sure SlicerOpener.py's AUTHORITATIVE_STORAGE_BASE_PATH matches

    STAFF_PASSWORD = os.environ.get('STAFF_PASSWORD') or 'defaultstaffpassword' # Change in production

    @staticmethod
    def init_app(app):
        # Ensure storage directories exist when the app initializes
        # This uses the APP_STORAGE_ROOT as defined in the app's config
        storage_root = app.config.get('APP_STORAGE_ROOT')
        if storage_root:
            required_dirs = [
                os.path.join(storage_root, 'Uploaded'),
                os.path.join(storage_root, 'Pending'),
                os.path.join(storage_root, 'ReadyToPrint'),
                os.path.join(storage_root, 'Printing'),
                os.path.join(storage_root, 'Completed'),
                os.path.join(storage_root, 'PaidPickedUp'),
                os.path.join(storage_root, 'thumbnails')
            ]
            for path in required_dirs:
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    # Log this error, as the app might not function correctly
                    # For now, print to console
                    print(f"Warning: Could not create directory {path}. Error: {e}")
        else:
            print("Warning: APP_STORAGE_ROOT is not configured. File operations may fail.")

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'app_dev.db')
    # Forcing a specific name for dev to avoid conflict if instance/app.db is used by a prod-like setup.

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False # Disable CSRF for tests

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(basedir), 'instance', 'app.db')
    # In production, instance/app.db could be on a network share, accessible by the single server instance.

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 