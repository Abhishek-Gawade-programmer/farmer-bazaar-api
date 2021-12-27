from django.urls import path, include
from .views import (
    CreateItemView,
    RetrieveItemView,
    CreateItemImageView,
    RetrieveItemImageView,
)

urlpatterns = [
    path("create-item/", CreateItemView.as_view(), name="create_item"),
    path("create-item-image/", CreateItemImageView.as_view(), name="create_item_image"),
    path(
        "get-item-image/<int:pk>/",
        RetrieveItemImageView.as_view(),
        name="get_item_image",
    ),
    path(
        "get-item-detail/<int:pk>/", RetrieveItemView.as_view(), name="get_item_detail"
    ),
]
