from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CreateUserView, SendUserOtpView, ValidateOtpView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="user_register"),
    path("send-otp-user/", SendUserOtpView.as_view(), name="send_otp_user"),
    path("validate-otp-user/", ValidateOtpView.as_view(), name="validate_otp_user"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
