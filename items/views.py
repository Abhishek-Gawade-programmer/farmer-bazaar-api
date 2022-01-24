from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from users.serializers import (
    CreateUserSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from users.models import User, PhoneOtp, UserProfile
from .serializers import (
    ItemSerializer,
    CategorySerializer,
    SubCategorySerializer,
    ItemRatingSerializer,
    ItemBagSerializer,
)
from .models import Item, ItemImage, Category, ItemRating, ItemBag, SubCategory
from users.permissions import IsOwnerOrReadOnly, IsOwnerOfItemBag
from django_filters import rest_framework as filters
from .filters import ItemFilter

# OPERATION ON ITEMS
class ListCreateItemView(generics.ListCreateAPIView):
    """Listing the item with pagination of 5 item with create"""

    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.filter(can_able_to_sell=True)
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ItemFilter

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class RetrieveUpdateDestroyItemView(generics.RetrieveUpdateDestroyAPIView):
    """get update destroy the item with permissions"""

    serializer_class = ItemSerializer
    # checking item call able to sell
    queryset = Item.objects.filter(can_able_to_sell=True)
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "item is deleted", "item_id": instance.id},
            status=status.HTTP_204_NO_CONTENT,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.data)
        return Response(
            {"detail": "Item is updated", "item_id": instance.id},
        )

    def get_permissions(self):
        # no permission for get request
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


# CATEGORY AND SUBCATEGORY

# CATEGORY LIST
class ListCategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# SUB CATEGORY LIST
class ListSubCategoryView(generics.ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer


# ITEM REVIEW
class GetReviewItemView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemRatingSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


# ITEM BAGS


class ItemBagCreateView(generics.CreateAPIView):
    # the owner of item only can create item bags
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfItemBag]


class ItemBagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    # the owner of item only can UD item bags
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfItemBag]

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
