from rest_framework.serializers import ValidationError
from django.utils import timezone


def validate_username(value):
    if len(value) != 10:
        raise ValidationError("Mobile Number Should Be 10 Digits")
    else:
        if not value.isdigit():
            raise ValidationError("Mobile Number Should Be  Numerical Value Only")


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
