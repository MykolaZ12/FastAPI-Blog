from config.celery_app import app
from app.user import services


@app.task()
def celery_send_reset_password_email(email_to: str, email: str, token: str):
    services.send_reset_password_email(email_to=email_to, email=email, token=token)


@app.task()
def celery_send_new_account_email(email_to: str, username: str, password: str):
    services.send_new_account_email(email_to=email_to, username=username, password=password)
