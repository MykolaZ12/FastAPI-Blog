from config import local_config

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

API_V1_STR = "/api/v1"
PROJECT_NAME = "Blog"

SECRET_KEY = local_config.SECRET_KEY
SERVER_HOST = "http://127.0.0.1:8000"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 5

# create superuser - python init_data.py
FIRST_SUPERUSER = "user@example.com"
FIRST_SUPERUSER_PASSWORD = "123456"

USERS_OPEN_REGISTRATION = True
EMAILS_ENABLED = True

EMAILS_FROM_NAME = local_config.EMAILS_FROM_NAME
EMAILS_FROM_EMAIL = local_config.EMAILS_FROM_EMAIL
EMAIL_TEMPLATES_DIR = "app/email-templates/build"

SMTP_HOST = local_config.SMTP_HOST
SMTP_PORT = local_config.SMTP_PORT
SMTP_TLS = local_config.SMTP_TLS
SMTP_USER = local_config.SMTP_USER
SMTP_PASSWORD = local_config.SMTP_PASSWORD

MEDIA_PATH = "media/user_image/"

