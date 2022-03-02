from rest_framework import serializers
from orders.models import OrderDetail


class OrderDetailOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ("",)
