from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from users.serializers import CreateUserSerializer, UserSerializer
from users.models import (
    User,
    PhoneOtp,
    UserProfile,
)
from .serializers import (
    ItemSerializer,
    ItemImageSerializer,
    ItemRatingSerializer,
    ItemBagSerializer,
    CategorySerializer,
    SubCategorySerializer,
    SellerReplySerializer,
    CategoryTypeSerializer,
)
from .models import (
    Item,
    ItemImage,
    Category,
    ItemRating,
    ItemBag,
    SubCategory,
    SellerReply,
    CategoryType,
)
from users.permissions import (
    IsOwnerOrReadOnly,
    IsOwnerOfObject,
    IsOwnerOfItemBelongs,
    IsAbleToSellItem,
    IsUnableRatingItem,
)
from django_filters import rest_framework as filters
from .filters import ItemFilter, CategoryTypeFilter
from rest_framework.filters import OrderingFilter

# OPERATION ON ITEMS
class ListCreateItemView(generics.ListCreateAPIView):
    """Listing the item with pagination of 5 item with create
    -Filtering Items

     Title name
     category name
     sub category name
     quantity unit and quantity

    -Ordering By
     average ratings
     quantity
     pricing for items bags

    """

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, IsAbleToSellItem]
    queryset = Item.objects.filter(can_able_to_sell=True)
    parser_classes = (MultiPartParser, FormParser)

    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    ordering_fields = ["average_rating", "quantity"]
    filterset_class = ItemFilter

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # creating the item
        serializer.save(user=self.request.user)


class RetrieveUpdateDestroyItemView(generics.RetrieveUpdateDestroyAPIView):
    """get update destroy the item with permissions"""

    serializer_class = ItemSerializer
    # checking item call able to sell
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsAbleToSellItem]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "item is deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )

    def get_permissions(self):
        # no permission for get request
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


# ITEM IMAGES
class ListCreateItemImageView(generics.ListCreateAPIView):
    # list the item with no permission or create the item who is owner of item
    serializer_class = ItemImageSerializer
    permission_classes = [IsAuthenticated, IsAbleToSellItem]
    queryset = ItemImage.objects.all()

    def get_object(self):
        # getting the object or 404 if item
        return get_object_or_404(Item, id=self.kwargs.get("pk"))

    def list(self, request, *args, **kwargs):
        # filtering the query  so that only item image will appear
        queryset = self.get_queryset().filter(item=self.get_object())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        # checking that item belongs to that ser
        if self.get_object().user == request.user:
            return self.create(request, *args, **kwargs)
        return Response(
            {"detail": "You permission to perform this action"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def perform_create(self, serializer):
        serializer.save(item=self.get_object())

    def get_permissions(self):
        # no permission for get request
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


class RetrieveUpdateDestroyItemImageView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAbleToSellItem, IsOwnerOfItemBelongs]
    serializer_class = ItemImageSerializer
    queryset = ItemImage.objects.all()

    def get_permissions(self):
        # no permission for get request
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


# CATEGORY AND SUBCATEGORY

# CATEGORY LIST
class ListCategoryView(generics.ListAPIView):
    pagination_class = None
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# SUB CATEGORY LIST
class ListSubCategoryView(generics.ListAPIView):
    pagination_class = None
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


#  CATEGORY TYPE LIST
class ListCategoryTypeView(generics.ListAPIView):
    pagination_class = None
    queryset = CategoryType.objects.all()
    serializer_class = CategoryTypeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CategoryTypeFilter


# ITEM REVIEW
class GetCreateReviewItemView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemRatingSerializer
    permission_classes = [IsAuthenticated, IsUnableRatingItem]
    lookup_field = "pk"

    def list(self, request, *args, **kwargs):
        # all review to get request
        instance = self.get_object()
        serializer = ItemRatingSerializer(instance.item_ratings.all(), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # creating the item review
        serializer.save(user=self.request.user, item=self.get_object())

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def post(self, request, *args, **kwargs):
        # checking user can't create comment on same item again
        qs = ItemRating.objects.filter(user=self.request.user, item=self.get_object())
        if qs.exists():
            return Response(
                {"detail": "You Can't Create Comment On Same Item Multiple Times"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return self.create(request, *args, **kwargs)


class RetrieveUpdateDestroyItemRatingView(generics.RetrieveUpdateDestroyAPIView):
    """Is user able to RUD item with permission"""

    serializer_class = ItemRatingSerializer
    queryset = ItemRating.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


class CreateSellerReplyView(generics.CreateAPIView):
    serializer_class = SellerReplySerializer
    queryset = ItemRating.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfItemBelongs, IsAbleToSellItem]

    def perform_create(self, serializer):
        # creating the seller reply on item review
        serializer.save(user=self.request.user)


# ITEM BAGS
class ItemBagCreateView(generics.CreateAPIView):
    # the owner of item only can create item bags
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfObject, IsAbleToSellItem]

    def get_object(self, item_id):
        item_obj = get_object_or_404(Item, id=item_id)
        self.check_object_permissions(self.request, item_obj)
        return item_obj

    def create(self, request, *args, **kwargs):
        self.get_object(request.data.get("item"))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class ItemBagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # the owner of item only can UD item bags
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfItemBelongs, IsAbleToSellItem]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


# GETTING ALL ITEM BAGS FROM ITEM
class AllItemBagItemView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemBagSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.bags.all(), many=True)
        return Response(serializer.data)


# Item Recommendation
class ListRecommendItemView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "pk"

    def get_queryset(self):
        current_item = get_object_or_404(Item, id=self.kwargs.get("pk"))
        # getting current_item farmer item  products of that category
        return current_item.user.my_items.exclude(id=current_item.id).filter(
            category=current_item.category, sub_category=current_item.sub_category
        )
