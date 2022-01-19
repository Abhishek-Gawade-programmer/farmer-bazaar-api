from django.urls import path, include
from .views import (
    ListCreateItemView,
    ListCategoryView,
    RetrieveUpdateDestroyItemView,
    RetrieveItemCategoryView,
    GetReviewItemView,
    RetrieveUpdateDestroyItemRatingView,
    ItemBagCreateListView,
)

urlpatterns = [
    path("create-list-item/", ListCreateItemView.as_view(), name="create_list_item"),
    path(
        "get-review-item/<int:pk>/", GetReviewItemView.as_view(), name="get_review_item"
    ),
    path(
        "get-delete-update-item/<int:pk>/",
        RetrieveUpdateDestroyItemView.as_view(),
        name="get_delete_update_item",
    ),
    path(
        "get-delete-update-item-rating/<int:pk>/",
        RetrieveUpdateDestroyItemRatingView.as_view(),
        name="get_delete_update_item-_rating",
    ),
    # path("all-items/", ListCreateItemView.as_view(), name="all_items"),
    path("all-categoty/", ListCategoryView.as_view(), name="all_categoty"),
    path(
        "sort-item-category/<str:category_name>/",
        RetrieveItemCategoryView.as_view(),
        name="all_category",
    ),
    # ITEM BAGS
    path(
        "create-list-item-bag/<int:pk>/",
        ItemBagCreateListView.as_view(),
        name="create_list_item_bag",
    ),
    # path(
    #     "get-item-detail/<int:pk>/", RetrieveItemView.as_view(), name="get_item_detail"
    # ),
    # path("update-item/<int:pk>/", UpdateItemView.as_view(), name="update_item_detail"),
    # path("delete-item/<int:pk>/", DestroyItemView.as_view(), name="delete_item"),
]
