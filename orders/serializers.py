from rest_framework import serializers
from users.models import Address
from .models import Order, OrderItem, OrderDetail
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


class OrderDetailSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())

    class Meta:
        model = OrderDetail
        fields = (
            "id",
            "order",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "payment_method",
        )
        extra_kwargs = {i: {"required": True} for i in fields}

    def create(self, validated_data):
        order_detail_qs = OrderDetail.objects.filter(order=validated_data.get("order"))
        if order_detail_qs.exists():
            raise serializers.ValidationError(
                "You can't Use Same Order For Order Details"
            )
        return super().create(validated_data)
