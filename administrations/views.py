from django.shortcuts import render, get_object_or_404, redirect

#  rest framework imports
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# serializers imports
from orders.serializers import OrderDetailSerializer

# model imports
from orders.models import OrderDetail

# permissions
from users.permissions import IsAdministerUser


class ListOrderDetailView(generics.ListAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsAdministerUser]


class ChangeOrderDetailOptions:
    pass
