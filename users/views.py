from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import CreateUserSerializer, UserSerializer, UserProfileSerializer
from .models import User, PhoneOtp, UserProfile, TermsAndCondition
from .permissions import IsOwnerOrReadOnly

# Create User
class CreateUserView(generics.CreateAPIView):
    serializer_class = CreateUserSerializer

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response(
            {"detail": "user is created"},
            status=status.HTTP_201_CREATED,
        )


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


class ValidateOtpView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        user_obj = get_object_or_404(User, username=phone_number)

        otp_text = request.data.get("otp_text")
        if otp_text:
            if otp_text.isdigit():
                qs_phone_otp = get_object_or_404(
                    PhoneOtp, user=user_obj, otp_code=otp_text
                )
                diff_time = timezone.now() - qs_phone_otp.updated
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


class RetrieveOtherUserDetailView(generics.RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class GetTermCondition(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def get(self, request, format=None):
        can_buy_product_text = TermsAndCondition.objects.get(
            title="can_buy_product"
        ).text
        return Response({"detail": can_buy_product_text})

    def post(self, request, format=None):
        user_profile_obj = request.user.user_profile
        user_profile_obj.can_buy_product = True
        user_profile_obj.buy_tc_accpeted = True
        user_profile_obj.save()
        return Response({"detail": "Buyer Access Added"})
