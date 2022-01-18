from django.urls import path, include
from .views import GetCartStatusView, AddUpdateItemToCartView, OrderItemRemoveCartView

urlpatterns = [
    path("get-cart-status/", GetCartStatusView.as_view(), name="get_cart_status"),
    path(
        "add-update-item-to-cart/<int:pk>/",
        AddUpdateItemToCartView.as_view(),
        name="add_item_to_cart",
    ),
    path(
        "delete-item-to-cart/<int:order_pk>/<int:order_item_pk>/",
        OrderItemRemoveCartView.as_view(),
        name="add_item_to_cart",
    ),
]
