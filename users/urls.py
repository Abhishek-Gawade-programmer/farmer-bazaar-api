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
    LogoutUserAPIView,
    TokenObtainPairWithoutPasswordView,
    RetrieveUpdateUserSellerNameView,
    RetrieveUpdateUserLanguageView,
)

urlpatterns = [
    # register the user
    path("register/", CreateUserView.as_view(), name="user_register"),
    # logout the user
    path("logout/", LogoutUserAPIView.as_view(), name="logout_user"),
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
    # change or get user seller name
    path(
        "get-update-user-seller-name/",
        RetrieveUpdateUserSellerNameView.as_view(),
        name="get_update_user_seller_name",
    ),
    # change Username(mobile number ) Password
    path("change-username/", ChangeUsernameView.as_view(), name="change_username"),
    # user langauage
    path(
        "get-set-user-language/",
        RetrieveUpdateUserLanguageView.as_view(),
        name="get_set_user_language",
    ),
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
