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
    ItemRatingSerializer,
    ItemBagSerializer,
)
from .models import Item, ItemImage, Category, ItemRating, ItemBag
from users.permissions import IsOwnerOrReadOnly, IsOwnerOfItemBag
from django_filters import rest_framework as filters
from .filters import ItemFilter
from .utils import convert_item_quantity_gram


class ListCreateItemView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ItemFilter

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)

        return Response(
            {"detail": "Item is created"},
            status=status.HTTP_201_CREATED,
        )


class RetrieveUpdateDestroyItemView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "item is deleted"}, status=status.HTTP_204_NO_CONTENT
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.data)
        return Response(
            {"detail": "Item is updated"},
        )

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]


class ListCategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class RetrieveItemCategoryView(generics.ListAPIView):
    lookup_field = "category_name"
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(category__name=self.kwargs.get("category_name"))
        return queryset


class GetReviewItemView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemRatingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ItemRatingSerializer(instance.item_ratings.all(), many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, item=self.get_object())

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def post(self, request, *args, **kwargs):
        qs = ItemRating.objects.filter(user=self.request.user, item=self.get_object())
        if qs.exists():
            return Response(
                {"detail": "You Can't Create Comment On Same Item Mutiple Times"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return self.create(request, *args, **kwargs)


class RetrieveUpdateDestroyItemRatingView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemRatingSerializer
    queryset = ItemRating.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class ItemBagCreateListView(generics.ListCreateAPIView):
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_item_object(self):
        item_obj = get_object_or_404(Item, pk=self.kwargs.get("pk"))
        return item_obj

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def filter_queryset(self, queryset, *args, **kwargs):

        queryset = self.get_queryset().filter(item=self.get_item_object())
        return queryset

    def create(self, request, *args, **kwargs):
        current_item = self.get_item_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.data
        item_gram_value = convert_item_quantity_gram(
            current_item.quantity_unit, current_item.quantity
        )
        item_bag_gram_value = convert_item_quantity_gram(
            valid_data.get("quantity_unit"), valid_data.get("quantity")
        )
        if item_bag_gram_value > item_gram_value:
            return Response(
                {
                    "detail": "Please check the quantity and unit of bag as Your item quantity and unit is excedting"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        item_bag_obj_qs = ItemBag.objects.filter(
            quantity=valid_data.get("quantity"),
            quantity_unit=valid_data.get("quantity_unit"),
            price=valid_data.get("price"),
            item=current_item,
        )
        if item_bag_obj_qs.exists():
            return Response(
                {"detail": "Bag is already Created"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            item_bag_obj = ItemBag.objects.create(
                quantity=valid_data.get("quantity"),
                quantity_unit=valid_data.get("quantity_unit"),
                price=valid_data.get("price"),
                item=current_item,
            )
            item_bag_obj.save()

            print(gram_value, "itrm quity unot ", current_item.quantity_unit)
            headers = self.get_success_headers(serializer.data)
            return Response(
                self.get_serializer(item_bag_obj).data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

    def post(self, request, *args, **kwargs):
        if self.get_item_object().user == request.user:
            return self.create(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


class ItemBagRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemBagSerializer
    queryset = ItemBag.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOfItemBag]

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]
