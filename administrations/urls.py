from django.urls import path, include
from .views import ListOrderDetailView, PaymentDoneByCODView

urlpatterns = [
    path(
        "payment-done-by-cod/",
        PaymentDoneByCODView.as_view(),
        name="payment_done_by_cod",
    ),
    # list all order details
    path(
        "list-order-details/",
        ListOrderDetailView.as_view(),
        name="list_order_details/",
    ),
]
