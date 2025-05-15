# app.py (root of project)
import os
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from app import create_app, extensions, config # Import models through create_app or extensions
from app.models.job import Job # Explicitly import Job model

config_name = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(config_name)

# Make db and Job available in shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return dict(db=extensions.db, Job=Job, app=app)

if __name__ == '__main__':
    # print(f"Starting app with FLASK_CONFIG: {config_name}") # Debug
    # print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}") # Debug
    # print(f"Storage Path: {app.config.get('STORAGE_PATH')}") # Debug
    app.run(debug=app.config.get('DEBUG', False)) 