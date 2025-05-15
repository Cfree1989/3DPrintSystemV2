# app/config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_should_be_changed'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')
    STORAGE_PATH = os.path.join(os.path.dirname(basedir), 'storage') # Path to the main storage directory
    # Ensure this path is correct for your shared network drive in production
    # e.g., STORAGE_PATH = 'Z:\\3DPrintFiles\\storage\' or '//SERVER/3DPrintFiles/storage'

    STAFF_PASSWORD = os.environ.get('STAFF_PASSWORD') or 'defaultstaffpassword' # Change in production

    @staticmethod
    def init_app(app):
        pass # Placeholder for app-specific config initialization

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