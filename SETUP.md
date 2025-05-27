# 3D Print System Setup Guide

## Environment Configuration (.env file)

Create a `.env` file in the project root with the following content:

```env
# 3D Print System Environment Configuration
# Flask Core Configuration
SECRET_KEY=GENERATE_YOUR_OWN_SECRET_KEY_HERE
FLASK_APP=app.py
FLASK_CONFIG=development
DEBUG=True

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///instance/app.db

# Storage Configuration
STORAGE_PATH=storage
APP_STORAGE_ROOT=storage

# Email Configuration (LSU Office 365)
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=coad-fablab@lsu.edu
MAIL_PASSWORD=COAD-DFABLAB
MAIL_DEFAULT_SENDER=coad-fablab@lsu.edu

# Base URL for confirmation links
BASE_URL=http://localhost:5000

# Staff Authentication
STAFF_PASSWORD=Fabrication
```

## Complete Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Cfree1989/3DPrintSystemV2.git
cd 3DPrintSystemV2
```

### 2. Create .env File
Create a `.env` file in the project root with the configuration above.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Storage Directories
```bash
mkdir storage
mkdir storage\Uploaded
mkdir storage\Pending
mkdir storage\ReadyToPrint
mkdir storage\Printing
mkdir storage\Completed
mkdir storage\PaidPickedUp
mkdir storage\thumbnails
```

### 5. Initialize Database
```bash
flask db upgrade
```

### 6. Run Application
```bash
python app.py
```

### 7. Access Application
- **Public Site**: http://localhost:5000
- **Staff Dashboard**: http://localhost:5000/dashboard
- **Staff Login**: Use password "Fabrication"

## Security Notes

- **IMPORTANT**: Generate your own SECRET_KEY using: `python -c "import secrets; print(secrets.token_hex(32))"`
- Replace `GENERATE_YOUR_OWN_SECRET_KEY_HERE` with your generated key
- Keep your .env file secure and never commit it to version control
- Change the STAFF_PASSWORD from "Fabrication" to something more secure for production
- Update email credentials with actual values for production deployment
- Never share your SECRET_KEY publicly or commit it to version control

## Troubleshooting

If you encounter issues:
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check that storage directories exist
3. Verify database is initialized: `flask db upgrade`
4. Confirm .env file is in the correct location (project root)
5. Check that Flask can import all modules without errors 