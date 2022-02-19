from django.urls import path, include
from .views import (
    GetCartStatusView,
    AddUpdateItemToCartView,
    OrderItemRemoveCartView,
    CheckOutOrderView,
)

urlpatterns = [
    # get the the user item bag status
    path(
        "get-create-cart-status/", GetCartStatusView.as_view(), name="get_cart_status"
    ),
    # checkout user order
    path("check-out-order/", CheckOutOrderView.as_view(), name="check_out_order"),
    # add or update order item from order
    path(
        "add-update-item-to-cart/",
        AddUpdateItemToCartView.as_view(),
        name="add_item_to_cart",
    ),
    # delete order item from order
    path(
        "delete-item-to-cart/<int:order_item_pk>/",
        OrderItemRemoveCartView.as_view(),
        name="add_item_to_cart",
    ),
]
