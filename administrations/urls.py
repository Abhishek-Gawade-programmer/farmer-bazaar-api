from django.urls import path, include
from .views import ListOrderDetailView

urlpatterns = [
    # list all order details
    path(
        "list-order-details/",
        ListOrderDetailView.as_view(),
        name="list_order_details/",
    ),
]
