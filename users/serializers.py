from rest_framework import serializers
from .models import User, PhoneOtp, UserProfile, Address
import django.contrib.auth.password_validation as validators
from rest_framework import exceptions
from rest_framework.response import Response
from django.utils import timezone
from rest_framework import status
from .validators import (
    validate_username,
    validate_first_name,
    validate_last_name,
    validate_atleast_18_age,
)
from rest_framework.validators import UniqueValidator


class CreateUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(validators=[validate_first_name])
    last_name = serializers.CharField(validators=[validate_last_name])
    password = serializers.CharField()
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all()), validate_username]
    )
    date_of_brith = serializers.DateField(
        source="user_profile.date_of_brith", validators=[validate_atleast_18_age]
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "password", "username", "date_of_brith")
        extra_kwargs = {i: {"required": True} for i in fields}

    def validate_password(self, value):
        errors = dict()
        try:
            validators.validate_password(password=value)

        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(value)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data.pop("username"),
            first_name=validated_data.pop("first_name"),
            last_name=validated_data.pop("last_name"),
        )
        user.is_active = False

        user.set_password(validated_data.pop("password"))
        user.save()
        profile_obj = UserProfile.objects.create(user=user)
        profile_obj.date_of_brith = validated_data.pop("user_profile").pop(
            "date_of_brith"
        )
        profile_obj.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(validators=[validate_first_name])
    last_name = serializers.CharField(validators=[validate_last_name])
    email = serializers.EmailField(max_length=50)
    username = serializers.CharField(
        validators=[validate_username, UniqueValidator(queryset=User.objects.all())],
        read_only=True,
    )
    # profile_pic = serializers.ImageField(allow_empty_file=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "username")
        extra_kwargs = {i: {"required": True} for i in fields}


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

        def create(self, validated_data):
            print(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    A student serializer to return the student details
    """

    user = UserSerializer()
    location = AddressSerializer()

    class Meta:
        model = UserProfile
        fields = ("user", "location")

    def update(self, instance, validated_data):
        user_data = validated_data.get("user")
        location_data = validated_data.get("location")
        if instance.location:
            address = AddressSerializer.update(
                AddressSerializer(),
                validated_data=location_data,
                instance=instance.location,
            )

        else:
            address = AddressSerializer.create(
                AddressSerializer(), validated_data=location_data
            )
        instance.location = address

        user = UserSerializer.update(
            UserSerializer(), validated_data=user_data, instance=instance.user
        )
        instance.user = user
        instance.save()
        userprofile_obj = UserProfile.objects.get(user=user)
        userprofile_obj.save()

        return userprofile_obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request.method == "GET":
            representation["profile_picture"] = request.build_absolute_uri(
                instance.profile_pic.url
            )

        return representation


# class NAMESerializer(serializers.):
# TODO: Define serializer fields here

# def create(self, validated_data):
#     print("jddfhjkdfj", validated_data)
#     return "dfkgdlfs"
# def save(self, validated_data):
#     print(validated_data)
#     return "dkfjglkd"

# class PhoneOtpSerializer(serializers.Serializer):
#     phone_number = serializers.CharField()
#     otp_text = serializers.IntegerField()

#     def validate_phone_number(self, value):
#         if not (len(value) == 10 and value.isdigit()):
#             raise serializers.ValidationError("Phone Number should be in proper format")
#         else:
#             qs = User.objects.filter(username=value)
#             if qs.exists():
#                 return super().validate(value)
#             else:
#                 raise serializers.ValidationError("Account Does not exist")

#     def validate_otp_text(self, value):

#         if not (len(str(value)) == 6):
#             raise serializers.ValidationError("Otp is not valid")
#         return super().validate(value)

#     def create(self, validated_data):
#         phone_number = validated_data.get("phone_number")
#         otp_text = validated_data.get("otp_text")
#         qs = User.objects.filter(username=phone_number)
#         if qs.exists():
#             # check if user exist in otp of
#             qs_phone_otp = PhoneOtp.objects.filter(user=qs[0])
#             if not qs_phone_otp.exists():
#                 phone_otp = PhoneOtp.objects.create(user=qs[0])
#                 phone_otp.save()
#                 phone_otp.send_phone_otp()

#                 return Response(
#                     {
#                         "detail": "OTP is sended",
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             else:
#                 diff_time = timezone.now() - qs_phone_otp[0].updated
#                 if ((diff_time.total_seconds()) // 60) < 2.0:
#                     return Response(
#                         {
#                             "detail": "Send After 5 Minutes ",
#                         },
#                         status=status.HTTP_400_BAD_REQUEST,
#                     )
#                 else:
#                     qs_phone_otp[0].save()
#                     qs_phone_otp[0].send_phone_otp()
#                     return Response(
#                         {
#                             "detail": "OTP is sended again",
#                         },
#                         status=status.HTTP_200_OK,
#                     )

#         else:
#             return Response(
#                 {
#                     "detail": "Account Not Found",
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         return
