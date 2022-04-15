from rest_framework import serializers

# django models
from orders.models import OrderDetail
from items.models import AdminCategory

# apps serializers imports
from items.serializers import CategoryTypeSerializer


class OrderDetailOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ("",)


class OrderDetailForCODSerializer(serializers.ModelSerializer):
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=OrderDetail.objects.filter(payment_method="COD")
    )

    class Meta:
        model = OrderDetail
        fields = ("order_id",)

    def validate(self, data):
        order_detail_instance = data.get("order_id")
        if not (
            order_detail_instance.order.dispatched
            and order_detail_instance.order.delivered
        ):
            raise serializers.ValidationError(
                "Order Must Be Dispatched And Delivered Before Paid"
            )
        if order_detail_instance.order.paid:
            raise serializers.ValidationError("Order Is Already Paid")
        return data


class AdminCategorySerializer(serializers.ModelSerializer):
    category_types = CategoryTypeSerializer(many=True)

    class Meta:
        model = AdminCategory
        fields = ("id", "image", "name", "category_types", "is_banner")
