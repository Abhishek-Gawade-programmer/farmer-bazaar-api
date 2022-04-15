from django.urls import path, include
from .views import (
    ListOrderDetailView,
    PaymentDoneByCODView,
    GetBannerCategoryView,
    ListAdminCategoryView,
)

urlpatterns = [
    # payment Done by COD
    path(
        "payment-done-by-cod/",
        PaymentDoneByCODView.as_view(),
        name="payment_done_by_cod",
    ),
    # latest banner for home srceen
    path(
        "get-banner-category/",
        GetBannerCategoryView.as_view(),
        name="get_banner_category",
    ),
    # list all order details
    path(
        "list-order-details/",
        ListOrderDetailView.as_view(),
        name="list_order_details/",
    ),
    # list all admin category
    path(
        "list-admin-category/",
        ListAdminCategoryView.as_view(),
        name="list_admin_category/",
    ),
]
