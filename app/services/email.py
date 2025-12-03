from app.core.config import settings

def send_email(email_to: str, subject: str, html_content: str):
    # Integration with SendGrid or SES would go here
    print(f"Sending email to {email_to} with subject {subject}")
    # Example:
    # message = Mail(
    #     from_email=settings.EMAILS_FROM_EMAIL,
    #     to_emails=email_to,
    #     subject=subject,
    #     html_content=html_content)
    # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    # response = sg.send(message)
    return True
