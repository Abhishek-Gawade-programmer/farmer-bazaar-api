from rest_framework import serializers
from .models import User
import django.contrib.auth.password_validation as validators
from rest_framework import exceptions


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "password", "username")
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

    def validate_username(self, value):
        if len(value) != 10:
            raise serializers.ValidationError("Mobile Number Should Be 10 Digits")
        else:
            if not value.isdigit():
                raise serializers.ValidationError(
                    "Mobile Number Should Be  Numerical Value Only"
                )
        return super().validate(value)

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First Name Should Be Alphabetic")
        return super().validate(value)

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last Name Should Be Alphabetic")
        return super().validate(value)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.is_active = False

        user.set_password(validated_data["password"])
        user.save()
        return user
