from django.contrib import admin
from .models import Order, OrderItem, OrderDetails

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderDetails)
