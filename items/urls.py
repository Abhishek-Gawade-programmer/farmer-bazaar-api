from django.urls import path, include
from .views import CreateItemView, RetrieveItemView, UpdateItemView, DestroyItemView

urlpatterns = [
    path("create-item/", CreateItemView.as_view(), name="create_item"),
    path(
        "get-item-detail/<int:pk>/", RetrieveItemView.as_view(), name="get_item_detail"
    ),
    path("update-item/<int:pk>/", UpdateItemView.as_view(), name="update_item_detail"),
    path("delete-item/<int:pk>/", DestroyItemView.as_view(), name="delete_item"),
]
