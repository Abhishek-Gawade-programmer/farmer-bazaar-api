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
    GetAcceptSellerTermCondition,
    ListCreateAddressView,
    GetSetUserDefaultAddress,
    RetrieveUpdateDestroyAddressView,
    ChangeUsernameView,
    TokenObtainPairWithoutPasswordView,
)

urlpatterns = [
    # register the user
    path("register/", CreateUserView.as_view(), name="user_register"),
    # login the user
    path(
        "token/", TokenObtainPairWithoutPasswordView.as_view(), name="token_obtain_pair"
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user-profile/", RetrieveUserProfileView.as_view(), name="user_profile"),
    path("send-otp-user/", SendUserOtpView.as_view(), name="send_otp_user"),
    path("validate-otp-user/", ValidateOtpView.as_view(), name="validate_otp_user"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "get-accept-seller-term-condition/",
        GetAcceptSellerTermCondition.as_view(),
        name="get_accept_seller_term_condition",
    ),
    # change Username(mobile number ) Password
    path("change-username/", ChangeUsernameView.as_view(), name="change_username"),
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
    path(
        "get-update-delete-address/<int:pk>/",
        RetrieveUpdateDestroyAddressView.as_view(),
        name="get_update_delete_address",
    ),
]
