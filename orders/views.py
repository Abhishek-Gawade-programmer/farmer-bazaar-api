from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, OrderDetail
from users.models import Address
from users.permissions import IsOwnerOfObject, IsAbleToSellItem, IsOwnerOfOrder
from .serializers import (
    OrderSerializer,
    OrderItemSerializer,
    CreateOrderItemSerializer,
    OrderDetailSerializer,
)
from django.http import HttpResponse

# HTML TO PDF
import os
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


class GetCartStatusView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # getting the status of cart
    def get(self, request, *args, **kwargs):
        # current user order or null
        order_or_null = request.user.user_profile.current_order
        if order_or_null:
            return Response(OrderSerializer(order_or_null).data)
        else:
            return Response(
                {"detail": "User Don't Have Active Order"}, status.HTTP_400_BAD_REQUEST
            )

    # creating the order
    def post(self, request, *args, **kwargs):
        order_or_null = request.user.user_profile.current_order
        # qs = Order.objects.filter(user=request.user, current_order=True)
        if order_or_null:
            order_instance = order_or_null
        else:
            order_instance = Order.objects.create(user=request.user)
            request.user.user_profile.current_order = order_instance
            request.user.user_profile.save()
            order_instance.save()
        return Response(OrderSerializer(order_instance).data, status.HTTP_201_CREATED)


class AddUpdateItemToCartView(generics.CreateAPIView):
    serializer_class = CreateOrderItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    def get_user_order(self):
        # try to get the current order or null
        return self.request.user.user_profile.current_order

    def post(self, request, *args, **kwargs):
        if self.get_user_order():
            return super().post(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "User Don't Have Any Active Orders"},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check_item_exists = OrderItem.objects.filter(
            order=self.get_user_order(), item_bag_id=serializer.data.get("item_bag")
        )
        if not check_item_exists.exists():
            # creating the new order item
            order_item_instance = OrderItem.objects.create(
                order=self.get_user_order(),
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
        order_or_null = self.request.user.user_profile.current_order
        if order_or_null:
            qs_order_item = OrderItem.objects.filter(
                order=order_or_null, id=kwargs.get("order_item_pk")
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


class CheckOutOrderView(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def check_user_permission(self, address_id):
        address_obj = get_object_or_404(Address, user=self.request.user, id=address_id)
        return address_obj

    def perform_create(self, serializer):
        # saving the order  to order detail to we can track the order
        order_or_null = self.request.user.user_profile.current_order
        address_obj = self.check_user_permission(self.request.POST.get("address"))
        serializer.save(order=order_or_null)

    def post(self, request, *args, **kwargs):
        # checking the order can able to placed
        order_or_null = self.request.user.user_profile.current_order
        if order_or_null == None:
            return Response(
                {"detail": "User Don't Have Any Active Order "},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # is order is empty or don't have any items
        if order_or_null.can_ableto_place():
            return super().post(request, *args, **kwargs)

        return Response(
            {
                "detail": "You can't Place The empty order or that Don't have order items"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# get order detail by id that have permission
class RetrieveOrderDetailView(generics.RetrieveAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfOrder]


# get order detail PDF by id that have permission
class RetrieveOrderInvoiceView(generics.RetrieveAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfOrder]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        from django.utils import timezone

        now_date = timezone.now()

        template_path = "invoice_pdf.html"
        context = {"order_detail": instance, "request": request, "now_date": now_date}
        # Create a Django response object, and specify content_type as pdf
        response = HttpResponse(content_type="application/pdf")
        response[
            "Content-Disposition"
        ] = f'attachment; filename="{request.user.get_full_name()}_invioce_number_{instance.id}.pdf"'
        # find the template and render it.
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")
        return response
