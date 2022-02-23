from django.urls import path, include
from .views import (
    ListCreateItemView,
    RetrieveUpdateDestroyItemView,
    GetCreateReviewItemView,
    RetrieveUpdateDestroyItemRatingView,
    ItemBagCreateView,
    RetrieveUpdateDestroyItemImageView,
    AllItemBagItemView,
    ItemBagRetrieveUpdateDestroyView,
    ListCreateItemImageView,
    ListCategoryView,
    ListSubCategoryView,
    CreateSellerReplyView,
    ListRecommendItemView,
)

urlpatterns = [
    # creating of list items
    path("create-list-item/", ListCreateItemView.as_view(), name="create_list_item"),
    # creating of list items
    path(
        "get-item-recommendations/<int:pk>/",
        ListRecommendItemView.as_view(),
        name="get_item_recommendations",
    ),
    # get the reviews of specific item
    path(
        "get-create-review-item/<int:pk>/",
        GetCreateReviewItemView.as_view(),
        name="get_create_review_item",
    ),
    # get the reviews of specific item
    path(
        "create-seller-reply/",
        CreateSellerReplyView.as_view(),
        name="create_seller_reply",
    ),
    # GET ITEM IMAGES OR CREATE ITEM IMAGES OF ITEM
    path(
        "get-item-images-create/<int:pk>/",
        ListCreateItemImageView.as_view(),
        name="get_item_images_create",
    ),
    # get update or destory th specific image of item
    path(
        "get-update-destory-item-image/<int:pk>/",
        RetrieveUpdateDestroyItemImageView.as_view(),
        name="getupdatedestrory_item_image",
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
    # CATGOIRES AND SUBCATGOIRES
    path("all-category/", ListCategoryView.as_view(), name="all_categoty"),
    path("all-subcategory/", ListSubCategoryView.as_view(), name="all_subcategoty"),
    # CREATE ITEM BAGS
    path(
        "create-item-bag/",
        ItemBagCreateView.as_view(),
        name="create_list_item_bag",
    ),
]
