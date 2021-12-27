from django.shortcuts import render, get_object_or_404
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
from .serializers import ItemSerializer, ItemImageSerializer, CreateItemSerializer
from .models import Item, ItemImage


class RetrieveItemImageView(generics.RetrieveAPIView):
    queryset = ItemImage.objects.all()
    serializer_class = ItemImageSerializer


class CreateItemView(generics.CreateAPIView):
    serializer_class = CreateItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # print(serializer.data)
        serializer.save()
        # super().create(request, *args, **kwargs)
        return Response(
            {
                "detail": "item is created",
            },
            status=status.HTTP_201_CREATED,
        )

    def create(self, request, *args, **kwargs):
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
