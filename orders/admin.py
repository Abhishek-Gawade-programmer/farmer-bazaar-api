from django.contrib import admin
from .models import Order, OrderItem, OrderDetail, PurchaseOnlineOrder

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderDetail)
admin.site.register(PurchaseOnlineOrder)
