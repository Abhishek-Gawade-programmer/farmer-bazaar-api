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
from .serializers import ItemSerializer, CategorySerializer
from .models import Item, ItemImage, Category
from users.permissions import IsOwnerOrReadOnly


class ListCreateItemView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        elif self.request.method == "GET":
            return []
        return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        # call the serializer create method
        super().create(request, *args, **kwargs)

        return Response(
            {
                "detail": "Item is created",
            },
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
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, serializer.data)
        return Response(
            {
                "detail": "Item is updated",
            },
        )

    def get_permissions(self):
        if self.request.method == "POST" or self.request.method == "PUT":
            return [IsAuthenticated()]
        elif self.request.method == "GET":
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


# queryset = self.queryset
# if isinstance(queryset, QuerySet):
#     queryset = queryset.filter(name=self.lookup_field)
# return queryset
