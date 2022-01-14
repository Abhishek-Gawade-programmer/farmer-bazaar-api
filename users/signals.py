from .models import User, UserProfile
from django.dispatch import receiver
from django.shortcuts import redirect
from django.db.models.signals import post_save
import requests
from django.core import files
from io import BytesIO


@receiver(post_save, sender=User)
def save_user_profile(sender, created, instance, **kwargs):
    print("IN SINGALS", sender, created, instance, kwargs)
# if created:
#     url = f"https://ui-avatars.com/api/?name={instance.first_name}+{instance.last_name}&size=256&bold=true&background=random"
#     response = requests.get(url)
#     fp = BytesIO()
#     fp.write(response.content)
#     qs = UserProfile.objects.filter(user=instance)
#     if qs.exists():
#         profile_obj = qs[0]
#     else:
#         profile_obj = UserProfile.objects.create(user=instance)
#     profile_obj.profile_pic.save(instance.username + ".png", files.File(fp))
#     profile_obj.save()
#     instance.save()

