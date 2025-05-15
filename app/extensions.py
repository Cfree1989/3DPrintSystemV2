# app/extensions.py

# Placeholder for Flask extensions initialization
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()

# print("Extensions (db, mail, migrate) initialized.") # Debug

# db = SQLAlchemy()
# mail = Mail()
# migrate = Migrate()

# print("Extensions (db, mail, migrate) initialized or placeholder created.") # Debug
pass 