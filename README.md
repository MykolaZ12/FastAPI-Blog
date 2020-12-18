# Used Stack
### Python 3.8
### FastAPI
### SqlAlchemy
### Celery
### Redis


# Features

* User Registration
* User Login & Logout
* User update profile & reset password
* Following users
* CRUD - Posts, Categories, Tags, Comments
* Search 
* Reply commetns
* Like posts
* Email subscription


# How To Start

### Clone the repository

```bash
git clone https://github.com/MykolaZ12/FastAPI-Blog.git
```

### Install requirements
```bash
pip install -r requirements.txt
```

### In config/ directory create local_config.py and fill by exemple
```bash
SECRET_KEY = "SECRET"

EMAILS_FROM_NAME = "Desired Name"
EMAILS_FROM_EMAIL = "your@email.com"

SMTP_HOST = "your mail server"
SMTP_PORT = 587
SMTP_TLS = True
SMTP_USER = "your@email.com"
SMTP_PASSWORD = "strong_password"


CELERY_BROKER_URL = 'redis://'
CELERY_RESULT_BACKEND = 'redis://'
```

### Create migrations & run migrations
```bash
alembic revision --autogenerate
alembic upgrade head
```

### Start Celery
Download and start redis or
```bash
docker run -d -p 6379:6379 redis
```
```bash
celery -A tasks worker --loglevel=INFO
```

### Start project
```bash
uvicorn main:app --reload
```