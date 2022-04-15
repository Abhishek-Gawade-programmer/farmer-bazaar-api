from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

# rest imports
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.conf import settings

# models imports
from .models import Order, OrderItem, OrderDetail
from items.models import ItemBag
from users.models import Address

from users.permissions import (
    IsOwnerOfObject,
    IsAbleToSellItem,
    IsOwnerOfOrder,
    IsAdministerUser,
)

# serializer imports
from .serializers import (
    OrderSerializer,
    OrderItemSerializer,
    CreateOrderItemSerializer,
    OrderDetailSerializer,
    RazorpayPayloadSerializer,
)

# other
import razorpay

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
            order_instance.save()
            request.user.user_profile.current_order = order_instance
            request.user.user_profile.save()
        return Response(OrderSerializer(order_instance).data, status.HTTP_201_CREATED)


class AddUpdateItemToCartView(generics.CreateAPIView):
    serializer_class = CreateOrderItemSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfObject]

    @property
    def get_user_order(self):
        # try to get the current order or null
        return self.request.user.user_profile.current_order

    def post(self, request, *args, **kwargs):
        if self.get_user_order:
            return super().post(request, *args, **kwargs)
        else:
            return Response(
                {"detail": "User Don't Have Any Active Orders"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_bag_obj = get_object_or_404(ItemBag, id=serializer.data.get("item_bag"))

        if item_bag_obj.item.user == request.user:
            return Response(
                {"detail": "You Can't Add ItemBag Of Your Item On Your Order"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # getting order items
        item_quantity_order = self.get_user_order.get_item_quantity(
            item_bag_obj.item
        ) + (item_bag_obj.convert_quantity_kg() * serializer.data.get("quantity"))

        check_item_exists = OrderItem.objects.filter(
            order=self.get_user_order, item_bag=item_bag_obj
        )
        if not check_item_exists.exists():

            if item_quantity_order > item_bag_obj.item.convert_quantity_kg():
                return Response(
                    {"detail": "You can't Purchase More Then Stock Available "},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # creating the new order item
            order_item_instance = OrderItem.objects.create(
                order=self.get_user_order,
                item_bag=item_bag_obj,
                quantity=serializer.data.get("quantity"),
            )
        else:
            # getting order items
            order_item_instance = check_item_exists[0]
            item_quantity_order = item_quantity_order - (
                order_item_instance.item_bag.convert_quantity_kg()
                * order_item_instance.quantity
            )
            if item_quantity_order > item_bag_obj.item.convert_quantity_kg():
                return Response(
                    {"detail": "You can't Purchase More Then Stock Available "},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # updating the same order item
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
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return Response(
                {"detail": "Order Number is Wrong Or User is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
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
        print("perform", order_or_null, self.request.user)
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
        if order_or_null.can_able_to_place():
            return super().post(request, *args, **kwargs)

        return Response(
            {
                "detail": "You can't Place The empty order or that Don't have order items"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# list the order of user that has not placed yet
class ListUserOrdersView(generics.ListAPIView):
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(order__user=self.request.user)
        return queryset


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
        # if error then show message
        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")
        return response


# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
)
# get order detail by id that have permission
class SetupPaymentClientView(generics.RetrieveAPIView):
    queryset = OrderDetail.objects.filter(payment_method="OP")
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfOrder]

    # setup of razorpay order
    def retrieve(self, request, *args, **kwargs):
        order_detail_instance = self.get_object()
        # if online order is not paid
        print("HOW ISN NOW WORKING", order_detail_instance.order.paid)
        if not order_detail_instance.order.paid:

            serializer = self.get_serializer(order_detail_instance)
            # create razorpay order
            amount = order_detail_instance.order.get_total_cost()
            payment = razorpay_client.order.create(
                {"amount": int(amount) * 100, "currency": "INR"}
            )
            ## TODO create Payment Model to store online payments orders

            return Response(
                {"payment": payment, "order_detail": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"detail": "Order Has Been Already Paid"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class HandlePaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RazorpayPayloadSerializer

    def post(self, request, *args, **kwargs):
        # {'razorpay_payment_id': '567', 'razorpay_order_id': '56756', 'razorpay_signature': '657567567'}
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer_data = serializer.data
        # TODO payment if exists in model
        order_detail_qs = OrderDetail.objects.filter(
            id=serializer_data.get("razorpay_order_id"), order__user=request.user
        )
        # allow payment
        if order_detail_qs.exists():
            # TRY AND EXCEPT CONDITION
            # checking the signature
            # check = razorpay_client.utility.verify_payment_signature(serializer_data)

            # if check is not None:
            #     print("Redirect to error url or error page")
            #     return Response(
            #         {"error": "Something went wrong"},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            # # if payment is successful that means check is None then we will turn isPaid=True
            # print("ORDER DETAIL serializer", .paid)
            order_obj = order_detail_qs[0].order
            order_obj.paid = timezone.now()
            order_obj.save()
            return Response(
                {"detail": "Payment Received Successfully"}, status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"detail": "Invalid Data"}, status=status.HTTP_400_BAD_REQUEST
            )
