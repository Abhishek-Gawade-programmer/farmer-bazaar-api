import random
from django.conf import settings
import requests
# from .models import User, UserProfile

# from django.core import files
# from io import BytesIO

def generate_otp(min_number, max_number):
    r = random.SystemRandom()
    return r.randint(min_number, max_number)


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


# def save_user_profile(sender, user):
#     url = f"https://ui-avatars.com/api/?name={user.first_name}+{user.last_name}&size=256&bold=true&background=random"
#     response = requests.get(url)
#     fp = BytesIO()
#     fp.write(response.content)

#     profile_obj = UserProfile.objects.get(user=user)
#     profile_obj.profile_pic.save(user.username + ".png", files.File(fp))
#     profile_obj.save()
#     user.save()
#     return redirect("choose_role")
#     print("sdhfjksdhfjsdjfhsdfh shgfhsdgh", user.stackholder)
