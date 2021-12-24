from django.contrib import admin
from .models import User, PhoneOtp, UserProfile

admin.site.register(User)
admin.site.register(PhoneOtp)
admin.site.register(UserProfile)
