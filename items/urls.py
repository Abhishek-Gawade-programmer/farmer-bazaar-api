from django.urls import path, include
from .views import (
    CreateItemView,
    RetrieveItemView,
    UpdateItemView,
    DestroyItemView,
    ListCreateItemView,
    ListCategoryView,
)

urlpatterns = [
    path("create-item/", CreateItemView.as_view(), name="create_item"),
    path("all-items/", ListCreateItemView.as_view(), name="all_items"),
    path("all-categoty/", ListCategoryView.as_view(), name="all_categoty"),
    path(
        "get-item-detail/<int:pk>/", RetrieveItemView.as_view(), name="get_item_detail"
    ),
    path("update-item/<int:pk>/", UpdateItemView.as_view(), name="update_item_detail"),
    path("delete-item/<int:pk>/", DestroyItemView.as_view(), name="delete_item"),
]
