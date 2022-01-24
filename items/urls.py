from django.urls import path, include
from .views import (
    ListCreateItemView,
    ListCategoryView,
    ListSubCategoryView,
    RetrieveUpdateDestroyItemView,
    GetReviewItemView,
    RetrieveUpdateDestroyItemRatingView,
    ItemBagCreateView,
    AllItemBagItemView,
    ItemBagRetrieveUpdateDestroyView,
)

urlpatterns = [
    # creating of list items
    path("create-list-item/", ListCreateItemView.as_view(), name="create_list_item"),
    # get the reviews of specific item
    path(
        "get-review-item/<int:pk>/", GetReviewItemView.as_view(), name="get_review_item"
    ),
    # RUD the of item
    path(
        "get-delete-update-item/<int:pk>/",
        RetrieveUpdateDestroyItemView.as_view(),
        name="get_delete_update_item",
    ),
    # RUD the of item review
    path(
        "get-delete-update-item-rating/<int:pk>/",
        RetrieveUpdateDestroyItemRatingView.as_view(),
        name="get_delete_update_item_rating",
    ),
    # CATGOIRES AND SUBCATGOIRES
    path("all-categoty/", ListCategoryView.as_view(), name="all_categoty"),
    path("all-subcategoty/", ListSubCategoryView.as_view(), name="all_subcategoty"),
    # CREATE ITEM BAGS
    path(
        "create-item-bag/",
        ItemBagCreateView.as_view(),
        name="create_list_item_bag",
    ),
    # ALL ITEM BAGS of ITEM
    path(
        "list-item-bag/<int:pk>/",
        AllItemBagItemView.as_view(),
        name="list_item_bag",
    ),
    # RUD ITEM BAG
    path(
        "get-update-delete-itembag/<int:pk>/",
        ItemBagRetrieveUpdateDestroyView.as_view(),
        name="get_update_delete_itembag",
    ),
]
