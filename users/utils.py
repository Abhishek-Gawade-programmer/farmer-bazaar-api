import random
from twilio.rest import Client


def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


def send_otp(otp_text, phone_number):
    account_sid = "AC1d49d283649b0f131f01d4561b37b630"
    auth_token = "650aa7fe22c7c507c95b69a080b7a2ec"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"OTP is {otp_text} it will be expire in 5 mins.",
        from_="+18555910421",
        to="+919503772231",
    )

    print(message.sid)
