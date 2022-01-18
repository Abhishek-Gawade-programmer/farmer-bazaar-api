from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ApiRoot

urlpatterns = [
    path("users/", include("users.urls")),
    path("items/", include("items.urls")),
    path("orders/", include("orders.urls")),
    path("", ApiRoot.as_view(), name="api_root"),
]
