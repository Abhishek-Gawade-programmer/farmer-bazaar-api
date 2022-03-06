from django.urls import path, include
from .views import ListItemStatisticsView,CustomerOrderViews

urlpatterns = [
    # list-item-statistics with image title and order reviews details of items
    path(
        "list-item-statistics/",
        ListItemStatisticsView.as_view(),
        name="list_item_statistics",
    ),
     # customer orders that are completed 
    path(
        "customer-orders/",
        CustomerOrderViews.as_view(),
        name="customer_orders",
    ),
]
