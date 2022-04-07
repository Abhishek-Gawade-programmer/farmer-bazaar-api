from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from .utils import validate_send_otp
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    AddressSerializer,
    PhoneOtpSerializer,
    ValidatePhoneOtpSerializer,
    TokenObtainPairWithoutPasswordSerializer,
    UserSellerNameSerializer,
)
from .models import User, PhoneOtp, UserProfile, TermsAndCondition, Address
from .permissions import IsOwnerOrReadOnly, IsAbleToSellItem, IsOwnerOfObject
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import logout


class TokenObtainPairWithoutPasswordView(TokenObtainPairView):
    serializer_class = TokenObtainPairWithoutPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# Create User
class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"detail": "user is created"}, status=status.HTTP_201_CREATED)


# activating user by otp
class SendUserOtpView(APIView):
    serializer_class = PhoneOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_phone_number = serializer.data.get("phone_number")
        response_fuc = validate_send_otp(user_phone_number)
        return Response(
            {"detail": response_fuc[0], "request_id": response_fuc[2]},
            status.HTTP_201_CREATED if response_fuc[1] else status.HTTP_400_BAD_REQUEST,
        )


# validate the Otp
class ValidateOtpView(APIView):
    serializer_class = ValidatePhoneOtpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.data
        qs_phone_otp = get_object_or_404(
            PhoneOtp,
            phone_number=serializer.data.get("phone_number"),
            otp_code=serializer.data.get("otp_code"),
            request_id=serializer.data.get("request_id"),
            is_verified=False,
        )
        if qs_phone_otp.can_able_to_use():
            # otp is verified
            qs_phone_otp.is_verified = True
            qs_phone_otp.save()
            # check that account exists or not for login or create account
            user_phone_qs = User.objects.filter(
                username=serializer.data.get("phone_number")
            )
            if user_phone_qs.exists():
                exists = True
            else:
                exists = False
            return Response(
                {"detail": "Account has been verified.", "exists": exists},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Otp Is Expired Resend It."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ChangeUsernameView(APIView):
    serializer_class = PhoneOtpSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        if phone_number:
            qs_phone_otp = get_object_or_404(User, username=user_phone)
        else:
            pass
        return Response(
            {"phone_number": ["This field is required."]},
            status=status.HTTP_400_BAD_REQUEST,
        )


# get update or edit user profile of request user
class RetrieveUserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get(id=self.request.user.id)
        return obj


# get the other user profile
class RetrieveOtherUserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RetrieveUpdateUserSellerNameView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAbleToSellItem]
    lookup_field = None
    serializer_class = UserSellerNameSerializer

    def get_object(self):
        return self.request.user


# accept the t and c for seller
class GetAcceptSellerTermCondition(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        can_buy_product_text = TermsAndCondition.objects.get(
            title="can_sell_product"
        ).text
        return Response({"detail": can_buy_product_text})

    def post(self, request, format=None):
        # accept the t and c for seller  for farmer
        seller_name = request.data.get("seller_name")
        if seller_name:
            user_profile_obj = request.user.user_profile
            user_profile_obj.seller_name = seller_name
            user_profile_obj.can_sell_product = True
            user_profile_obj.seller_tc_accepted = True
            user_profile_obj.save()
            return Response({"detail": "Seller Access Added"})
        else:
            return Response(
                {"seller_name": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Create A New Address or list address user  Of User
class ListCreateAddressView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    queryset = Address.objects.all()
    pagination_class = None

    def perform_create(self, serializer):
        address_obj = serializer.save(user=self.request.user)
        # setting the default address to user if not exist (the first address as a default)
        user_profile = self.request.user.user_profile
        if not user_profile.default_address:
            user_profile.default_address = address_obj
            user_profile.save()

    def list(self, request, *args, **kwargs):
        # filtering the address which have user
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Get or SET User Default Address
class GetSetUserDefaultAddress(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # checking that user have the default address
        get_default_address_null = request.user.user_profile.default_address
        if get_default_address_null:
            return Response(AddressSerializer(get_default_address_null).data)
        else:
            return Response(
                {"detail": "User Don't Have Default Address"},
                status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, *args, **kwargs):
        address_id = request.data.get("address_id")
        if address_id:
            address_obj = get_object_or_404(Address, id=address_id, user=request.user)
            request.user.user_profile.default_address = address_obj
            request.user.user_profile.save()
            return Response({"detail": "Added To Default Address"})

        else:
            return Response(
                {"address_id": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RetrieveUpdateDestroyAddressView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == request.user.user_profile.default_address:
            return Response(
                {"detail": "Can't Delete Default Address"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LogoutUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):

        logout(request)
        return Response(
            {"success": "Successfully logged out."}, status=status.HTTP_200_OK
        )
