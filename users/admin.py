from django.contrib import admin
from .models import User, PhoneOtp, UserProfile, Address, TermsAndCondition

admin.site.register(User)
admin.site.register(Address)
admin.site.register(PhoneOtp)
admin.site.register(UserProfile)
admin.site.register(TermsAndCondition)
