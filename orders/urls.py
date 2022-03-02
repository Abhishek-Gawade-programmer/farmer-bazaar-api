from django.urls import path, include
from .views import (
    GetCartStatusView,
    AddUpdateItemToCartView,
    OrderItemRemoveCartView,
    CheckOutOrderView,
    RetrieveOrderDetailView,
    RetrieveOrderInvoiceView,
    ListUserOrdersView,
)

urlpatterns = [
    # get the the user item bag status
    path(
        "get-create-cart-status/", GetCartStatusView.as_view(), name="get_cart_status"
    ),
    # user order list (my orders)
    path("user-orders-list/", ListUserOrdersView.as_view(), name="user-orders-list"),
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
    # get the order info
    path(
        "get-order-detail/<int:pk>/",
        RetrieveOrderDetailView.as_view(),
        name="get_order_detail",
    ),
    # get the order  detail pdfinfo
    path(
        "get-order-invoice-pdf/<int:pk>/",
        RetrieveOrderInvoiceView.as_view(),
        name="get_order_invoice_pdf",
    ),
]
