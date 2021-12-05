from rest_framework.serializers import ValidationError


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
