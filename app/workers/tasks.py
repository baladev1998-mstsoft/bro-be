from celery import shared_task
import time

@shared_task
def send_email(email_to: str, subject: str = "", html_content: str = ""):
    # Simulate email sending
    time.sleep(1)
    print(f"Email sent to {email_to}: {subject}")
    return True

@shared_task
def send_sms(phone_number: str, message: str):
    # Simulate SMS sending
    time.sleep(1)
    print(f"SMS sent to {phone_number}: {message}")
    return True
