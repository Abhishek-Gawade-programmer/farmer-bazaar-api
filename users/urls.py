from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    CreateUserView,
    SendUserOtpView,
    ValidateOtpView,
    RetrieveUserProfileView,
    RetrieveOtherUserDetailView,
    GetTermCondition,
    ListCreateAddressView,
    GetSetUserDefaultAddress,
)

urlpatterns = [
    # register the user
    path("register/", CreateUserView.as_view(), name="user_register"),
    # login the user
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "user-profile/<int:pk>/",
        RetrieveOtherUserDetailView.as_view(),
        name="user_profile_id",
    ),
    path("user-profile/", RetrieveUserProfileView.as_view(), name="user_profile"),
    path("send-otp-user/", SendUserOtpView.as_view(), name="send_otp_user"),
    path("validate-otp-user/", ValidateOtpView.as_view(), name="validate_otp_user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("get-term-condition/", GetTermCondition.as_view(), name="get_term_condition"),
    path(
        "create-get-address/",
        ListCreateAddressView.as_view(),
        name="create_get_address",
    ),
    path(
        "get-set-default-address/",
        GetSetUserDefaultAddress.as_view(),
        name="get_set_default_address",
    ),
]
