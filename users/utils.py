import random
from django.conf import settings
import requests

import json

# genertaing the radom otp to user
def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


# validating before sending otp
def validate_send_otp(user_phone_number: str):
    from .models import PhoneOtp
    from django.utils import timezone

    qs_phone_otp = PhoneOtp.objects.filter(phone_number=user_phone_number)

    if qs_phone_otp.exists():
        if qs_phone_otp[0].can_able_to_use():
            return ("Wait Till 5 Minutes ", False, None)
        else:
            qs_phone_otp[0].send_phone_otp()
            return ("Otp Is Sended Again ", True, qs_phone_otp[0].request_id)
    else:
        phone_otp = PhoneOtp.objects.create(phone_number=user_phone_number)
        phone_otp.send_phone_otp()
        return ("OTP is sended", True, phone_otp.request_id)


# sending the otp user mobile number
def send_otp(otp_text, phone_number):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": settings.FAST_API_KEY,
        "variables_values": f"{otp_text}",
        "route": "otp",
        "numbers": f"{phone_number}",
    }
    response = requests.request(
        "GET", url, headers={"cache-control": "no-cache"}, params=querystring
    )

    return json.loads(response.text).get("request_id")
