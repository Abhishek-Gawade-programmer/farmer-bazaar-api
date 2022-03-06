from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# serializers imports
from .serializers import ShortItemStatisticSerializer
from orders.serializers import OrderItemSerializer

# model imports
from items.models import Item
from orders.models import OrderItem

# permissions imports

from users.permissions import IsAbleToSellItem

# it Shows The Items With Image Title And Statistics Details
class ListItemStatisticsView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ShortItemStatisticSerializer
    permission_classes = [IsAuthenticated, IsAbleToSellItem]

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        return queryset


# Customer Orders (Orders in which the item of farmers ) OrderItem
class CustomerOrderViews(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated, IsAbleToSellItem]

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset().filter(item_bag__item__user=self.request.user)
            .exclude(
                order__placed=None,
                order__paid=None,
                order__dispatched=None,
                order__delivered=None,
            )
        )
        return queryset
