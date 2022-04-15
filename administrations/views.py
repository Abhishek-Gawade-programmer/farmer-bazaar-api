from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

#  rest framework imports
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

# serializers imports
from orders.serializers import OrderDetailSerializer
from .serializers import OrderDetailForCODSerializer, AdminCategorySerializer

# model imports
from orders.models import OrderDetail
from items.models import AdminCategory

# permissions
from users.permissions import IsAdministerUser


class ListOrderDetailView(generics.ListAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsAdministerUser]


class ChangeOrderDetailOptions:
    pass


class PaymentDoneByCODView(APIView):
    # permission_classes = [IsAuthenticated, IsAdministerUser]
    serializer_class = OrderDetailForCODSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_detail_instance = serializer.validated_data.get("order_id")
        order_detail_instance.order.paid = timezone.now()
        order_detail_instance.order.save()

        return Response(
            {"detail": "Order Has Been Paid By Cash On Delivery"},
            status=status.HTTP_200_OK,
        )


class GetBannerCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        banner_category = AdminCategory.objects.filter(is_banner=True).last()
        if banner_category:
            serializer_data = AdminCategorySerializer(banner_category).data
            return Response(serializer_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"detail": "No Banner Has Been Set"}, status=status.HTTP_400_BAD_REQUEST
            )


class ListAdminCategoryView(generics.ListAPIView):
    queryset = AdminCategory.objects.all()
    serializer_class = AdminCategorySerializer
