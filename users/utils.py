import random
from django.conf import settings
import requests


# genertaing the radom otp to user
def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


# validating before sending otp
def validate_send_otp(user_phone):
    from .models import PhoneOtp
    from django.utils import timezone

    qs_phone_otp = PhoneOtp.objects.filter(user=user_phone)

    if qs_phone_otp.exists():
        diff_time = timezone.now() - qs_phone_otp[0].updated
        if ((diff_time.total_seconds()) // 60) < 2.0:
            return ("Wait Till 5 Minutes ", False)
        else:
            qs_phone_otp[0].save()
            qs_phone_otp[0].send_phone_otp()
            return ("Otp Is Sended Again ", False)
    else:
        phone_otp = PhoneOtp.objects.create(user=user_phone)
        phone_otp.save()
        phone_otp.send_phone_otp()
        return ("OTP is sended", True)


# sending the otp user mobile number
def send_otp(otp_text, phone_number):
    url = "https://www.fast2sms.com/dev/bulkV2"

    querystring = {
        "authorization": settings.FAST_API_KEY,
        "variables_values": f"{otp_text}",
        "route": "otp",
        "numbers": f"{phone_number}",
    }

    headers = {"cache-control": "no-cache"}

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    return
