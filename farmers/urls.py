from django.urls import path, include
from .views import ListItemStatisticsView

urlpatterns = [
    # list-item-statistics with image title and order reviews details of items
    path(
        "list-item-statistics/",
        ListItemStatisticsView.as_view(),
        name="list_item_statistics",
    ),
]
