from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from .serializers import (
    CreateUserSerializer,
    UserSerializer,
    UserProfileSerializer,
    AddressSerializer,
)
from .models import User, PhoneOtp, UserProfile, TermsAndCondition, Address
from .permissions import IsOwnerOrReadOnly, IsAbleToSellItem

# Create User
class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({"detail": "user is created"}, status=status.HTTP_201_CREATED)


# activating user by otp
class SendUserOtpView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        if phone_number and len(phone_number) == 10 and phone_number.isdigit():
            qs = User.objects.filter(username=phone_number)
            if qs.exists():
                # check if user exist in otp of
                qs_phone_otp = PhoneOtp.objects.filter(user=qs[0])
                if not qs_phone_otp.exists():
                    phone_otp = PhoneOtp.objects.create(user=qs[0])
                    phone_otp.save()
                    phone_otp.send_phone_otp()

                    return Response(
                        {"detail": "OTP is sended"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    diff_time = timezone.now() - qs_phone_otp[0].updated
                    if ((diff_time.total_seconds()) // 60) < 2.0:
                        return Response(
                            {"detail": "Send After 5 Minutes "},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    else:
                        qs_phone_otp[0].save()
                        qs_phone_otp[0].send_phone_otp()
                        return Response(
                            {"detail": "OTP is sended again"},
                            status=status.HTTP_200_OK,
                        )

            else:
                return Response(
                    {"detail": "Account Not Found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        elif not (len(phone_number) == 10 and phone_number.isdigit()):
            return Response(
                {"detail": ["Enter valid Phone Number"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        else:
            return Response(
                {"phone_number": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# validate the Otp
class ValidateOtpView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        otp_text = request.data.get("otp_text")
        if otp_text:
            user_obj = get_object_or_404(User, username=phone_number)
            if otp_text.isdigit():
                qs_phone_otp = get_object_or_404(
                    PhoneOtp, user=user_obj, otp_code=otp_text
                )
                diff_time = timezone.now() - qs_phone_otp.updated
                # checking that the otp in less that 2 minutes
                if ((diff_time.total_seconds()) // 60) < 2.0:
                    user_obj.is_active = True
                    user_obj.save()

                    return Response(
                        {"detail": "Account has been verified."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"detail": "Otp Is Expired Resend It."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                qs_phone_otp.delete()

            else:
                return Response(
                    {"otp_text": ["Not a valid Otp"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"otp_text": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )


# get update or edit user profile of request user
class RetrieveUserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get(user=self.request.user)
        return obj

    def perform_update(self, serializer):
        serializer.save()


# get the other user profile
class RetrieveOtherUserDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


# accept the t and c for seller
class GetTermCondition(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        can_buy_product_text = TermsAndCondition.objects.get(
            title="can_sell_product"
        ).text
        return Response({"detail": can_buy_product_text})

    def post(self, request, format=None):
        # accept the t and c for seller ie for farmer
        user_profile_obj = request.user.user_profile
        user_profile_obj.can_sell_product = True
        user_profile_obj.seller_tc_accepted = True
        user_profile_obj.save()
        return Response({"detail": "Seller Access Added"})


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
