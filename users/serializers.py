from rest_framework import serializers
from .models import User, PhoneOtp, UserProfile, Address
import django.contrib.auth.password_validation as validators
from rest_framework import exceptions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from .validators import (
    validate_username_login,
    validate_first_name,
    validate_last_name,
    validate_atleast_18_age,
    validate_username_exist,
    validate_phone_number_otp_send,
)
from rest_framework.validators import UniqueValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import RegexValidator, MinLengthValidator







class TokenObtainPairWithoutPasswordSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(
            validators=[
                MinLengthValidator(10),
                RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
                validate_username_login,
            ]
        )
        self.fields["password"].required = False
        self.fields["request_id"] = serializers.CharField(max_length=30)

    def validate(self, attrs):

        # check  phone otp exists
        get_object_or_404(
            PhoneOtp,
            phone_number=attrs.get("username"),
            request_id=attrs.get("request_id"),
        )
        self.user = get_object_or_404(User, username=attrs.get("username"))
        refresh = RefreshToken.for_user(self.user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class CreateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(validators=[validate_first_name])
    last_name = serializers.CharField(validators=[validate_last_name])
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
            validate_username_login,
        ]
    )
    date_of_brith = serializers.DateField(
        source="user_profile.date_of_brith", validators=[validate_atleast_18_age]
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "date_of_brith")
        extra_kwargs = {i: {"required": True} for i in fields}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.pop("username"),
            first_name=validated_data.pop("first_name"),
            last_name=validated_data.pop("last_name"),
        )
        user.is_active = True
        user.set_unusable_password()
        user.save()
        profile_obj = UserProfile.objects.create(user=user)
        profile_obj.date_of_brith = validated_data.pop("user_profile").pop(
            "date_of_brith"
        )
        profile_obj.save()
        return user
class UserSellerNameSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(max_length=50,source="user_profile.seller_name")
    class Meta:
        model = User
        fields = ("seller_name",)
        extra_kwargs = {i: {"required": True} for i in fields}
    def update(self, instance, validated_data):
        instance.user_profile.seller_name=validated_data.get("user_profile").get("seller_name")
        instance.user_profile.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(validators=[validate_first_name])
    last_name = serializers.CharField(validators=[validate_last_name])
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(
        validators=[
            validate_username_login,
            UniqueValidator(queryset=User.objects.all()),
        ],
        read_only=True,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")
        extra_kwargs = {i: {"required": True} for i in fields}


class PhoneOtpSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )

    class Meta:
        model = PhoneOtp
        fields = ("phone_number",)


class ValidatePhoneOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
            validate_phone_number_otp_send,
        ],
    )
    request_id = serializers.CharField(max_length=30)
    otp_code = serializers.CharField(
        max_length=10,
        validators=[
            MinLengthValidator(6),
            RegexValidator(regex=r"^\d*$", message="Only 6 digits are allowed."),
        ],
    )


class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Address
        fields = (
            "id",
            "full_address",
            "short_address",
            "place_id",
            "latitude",
            "longitude",
            "postal_code",
            "user",
            "updated",
            "created",
        )
