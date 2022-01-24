from rest_framework import serializers
from .models import Order, OrderItem
from items.models import Item, ItemBag
from items.serializers import ItemShortSerializer, ItemBagSerializer


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
        if not item_bag_obj.available_status:
            raise serializers.ValidationError("This bag is currently unavailable")
        return data


class OrderSerializer(serializers.ModelSerializer):
    order_items_all = OrderItemSerializer(source="order_items", many=True)
    order_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)

    def get_order_cost(self, obj):
        return obj.get_total_cost()
