from rest_framework.serializers import ValidationError
from django.utils import timezone
from .models import User, PhoneOtp


def validate_username_login(value):
    qs_phone_otp = PhoneOtp.objects.filter(phone_number=value, is_verified=True)
    if qs_phone_otp.exists():
        if not qs_phone_otp[0].can_able_to_authenticate():
            raise ValidationError("Timeout Please Send OTP Again")

    else:
        raise ValidationError("Phone Number is Not Verified")


def validate_phone_number_otp_send(value):
    qs_phone_otp = PhoneOtp.objects.filter(phone_number=value)
    if not qs_phone_otp.exists():
        raise ValidationError("Otp is Not send to This Phone Number")


def validate_username_exist(value):
    qs = User.objects.filter(username=value)
    if not qs.exists():
        raise ValidationError("No Account Found With Given Credentials ")


def validate_first_name(value):
    if not value.isalpha():
        raise ValidationError("First Name Should Be Alphabetic")


def validate_last_name(value):
    if not value.isalpha():
        raise ValidationError("Last Name Should Be Alphabetic")


def validate_atleast_18_age(value):
    diff_date = timezone.now().date() - value
    if (diff_date.days // 365) < 18:
        raise ValidationError("Must Have Atleast 18 Age")
    elif (diff_date.days // 365) > 100:
        raise ValidationError("Please Enter Valid Date Of Brith")
