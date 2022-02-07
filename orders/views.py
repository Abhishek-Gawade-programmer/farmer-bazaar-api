from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from users.permissions import IsOwnerOfObject, IsAbleToSellItem
from .serializers import OrderSerializer, OrderItemSerializer, CreateOrderItemSerializer


class GetCartStatusView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # getting the status of cart
    def get(self, request, *args, **kwargs):
        qs = Order.objects.filter(user=request.user, current_order=True)
        if qs.exists():
            order_instance = qs[0]
            return Response(OrderSerializer(order_instance).data)
        else:
            return Response(
                {"detail": "User Don't Have Active Order"}, status.HTTP_400_BAD_REQUEST
            )

    # creating the order
    def post(self, request, *args, **kwargs):
        qs = Order.objects.filter(user=request.user, current_order=True)
        if qs.exists():
            order_instance = qs[0]
        else:
            order_instance = Order.objects.create(user=request.user)
            order_instance.current_order = True
        order_instance.save()
        return Response(OrderSerializer(order_instance).data, status.HTTP_201_CREATED)


class AddUpdateItemToCartView(generics.CreateAPIView):
    serializer_class = CreateOrderItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    def post(self, request, *args, **kwargs):
        qs = Order.objects.filter(
            current_order=True, pk=kwargs.get("order_pk"), user=request.user
        )
        if qs.exists():
            return super().post(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "Order Number is Wrong Or User is invalid"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_item_exists = OrderItem.objects.filter(
            order_id=kwargs.get("order_pk"), item_bag_id=serializer.data.get("item_bag")
        )
        if not check_item_exists.exists():
            # creating the new order item
            order_item_instance = OrderItem.objects.create(
                order_id=kwargs.get("order_pk"),
                item_bag_id=serializer.data.get("item_bag"),
                quantity=serializer.data.get("quantity"),
            )
        else:
            # updating the same order item
            order_item_instance = check_item_exists[0]
            order_item_instance.quantity = serializer.data.get("quantity")
        order_item_instance.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            OrderItemSerializer(order_item_instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class OrderItemRemoveCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        qs = Order.objects.filter(
            current_order=True, pk=kwargs.get("order_pk"), user=request.user
        )
        if qs.exists():
            qs_order_item = OrderItem.objects.filter(
                order_id=qs[0].id, id=kwargs.get("order_item_pk")
            )
            if qs_order_item.exists():
                qs_order_item[0].delete()
                return Response(
                    {"detail": "Order Item is deleted"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"detail": "Order Item Number is Wrong "},
                    status=status.HTTP_404_NOT_FOUND,
                )

        else:
            return Response(
                {"detail": "Order Number is Wrong Or User is invalid"},
                status=status.HTTP_404_NOT_FOUND,
            )
