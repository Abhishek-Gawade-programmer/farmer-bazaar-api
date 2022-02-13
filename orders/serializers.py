from rest_framework import serializers
from .models import Order, OrderItem, OrderDetails
from items.models import Item, ItemBag
from items.serializers import ItemShortSerializer, ItemBagSerializer


class OrderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = (
            "id",
            "order",
            "first_name",
            "phone_number",
            "address",
            "payment_method",
        )


class OrderItemSerializer(serializers.ModelSerializer):
    item_bag = ItemBagSerializer()

    class Meta:
        model = OrderItem
        fields = "__all__"


class CreateOrderItemSerializer(serializers.ModelSerializer):
    item_bag = serializers.PrimaryKeyRelatedField(queryset=ItemBag.objects.all())

    class Meta:
        model = OrderItem
        fields = ("quantity", "item_bag")
        extra_kwargs = {i: {"required": True} for i in fields}

    def validate(self, data):
        item_bag_obj = data.get("item_bag")
        number_of_available_bags = item_bag_obj.number_of_available()
        if number_of_available_bags < data.get("quantity"):
            raise serializers.ValidationError(
                f"The quantity must at most {number_of_available_bags}"
            )

        if not item_bag_obj.available_status:
            raise serializers.ValidationError("This bag is currently unavailable")
        return data


class OrderSerializer(serializers.ModelSerializer):
    order_items_all = OrderItemSerializer(source="order_items", many=True)
    order_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "order_items_all",
            "order_cost",
            "placed",
            "paid",
            "dispatched",
            "delivered",
            "rejected",
            "reject_reason",
            "current_order",
            "updated",
            "created",
        )

    def get_order_cost(self, obj):
        return obj.get_total_cost()
