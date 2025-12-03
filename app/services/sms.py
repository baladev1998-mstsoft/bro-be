from app.core.config import settings

def send_sms(phone_number: str, message: str):
    # Integration with Twilio would go here
    print(f"Sending SMS to {phone_number}: {message}")
    # Example:
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(
    #     body=message,
    #     from_=settings.TWILIO_PHONE_NUMBER,
    #     to=phone_number
    # )
    return True
