from django.contrib import admin
from .models import Order, OrderItem, OrderDetail

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderDetail)
