from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from users.serializers import (
    CreateUserSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from users.models import User, PhoneOtp, UserProfile
from .serializers import ItemSerializer, CategorySerializer
from .models import Item, ItemImage, Category
from users.permissions import IsOwnerOrReadOnly


class CreateItemView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # call the serializer create method
        super().create(request, *args, **kwargs)

        return Response(
            {
                "detail": "Item is created",
            },
            status=status.HTTP_201_CREATED,
        )


class RetrieveItemView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class UpdateItemView(generics.UpdateAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

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


class ListCreateItemView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()


class DestroyItemView(generics.DestroyAPIView):
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "item is deleted"}, status=status.HTTP_204_NO_CONTENT
        )


class ListCategoryView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
