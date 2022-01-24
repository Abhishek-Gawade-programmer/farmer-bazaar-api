import random
from django.conf import settings
import requests

# genertaing the radom otp to user
def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


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
