import random
from twilio.rest import Client
from django.conf import settings


def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


def send_otp(otp_text, phone_number):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"OTP is {otp_text} it will be expire in 5 mins.",
        from_=settings.TWILIO_AUTH_NUMBER,
        to=settings.MY_NUMBER,
    )

    print(message.sid)
