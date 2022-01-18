from rest_framework import serializers
from .models import Order, OrderItem
from items.models import Item
from items.serializers import ItemShortSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemShortSerializer()

    class Meta:
        model = OrderItem
        fields = "__all__"


class CreateOrderItemSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = OrderItem
        fields = ("quantity", "quantity_unit", "item")
        extra_kwargs = {i: {"required": True} for i in fields}

    def validate(self, data):
        current_order_item = data["item"]
        quantity = data["quantity"]
        quantity_unit = data["quantity_unit"]

        if current_order_item.quantity < quantity:
            raise serializers.ValidationError(
                f"Quantity Have A Limit Max To {current_order_item.quantity}"
            )
        if current_order_item.quantity_unit != quantity_unit:
            raise serializers.ValidationError(
                f"Quantity Unit Must Be {current_order_item.quantity_unit}"
            )
        return data


class OrderSerializer(serializers.ModelSerializer):
    order_items_all = OrderItemSerializer(source="order_items", many=True)
    order_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)

    def get_order_cost(self, obj):
        return obj.get_total_cost()
