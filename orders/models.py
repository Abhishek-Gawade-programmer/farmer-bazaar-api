from django.db import models
from users.models import User
from items.models import Item, LABEL_UNIT_CHOICES
from django.core.validators import MinValueValidator


class Order(models.Model):
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.SET_NULL,
        null=True,
    )
    placed = models.DateTimeField(null=True, blank=True)
    paid = models.DateTimeField(null=True, blank=True)
    # payment status
    dispatched = models.DateTimeField(null=True, blank=True)
    delivered = models.DateTimeField(null=True, blank=True)
    rejected = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(max_length=1000, blank=True)
    current_order = models.BooleanField(default=False, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def get_total_cost(self):
        total_cost = 0
        for order_item in self.order_items.all():
            total_cost += order_item.cost
        return total_cost

    def __str__(self):
        return self.user.username + "  Order -->   " + str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        Item, related_name="active_orders", on_delete=models.CASCADE
    )
    quantity = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    quantity_unit = models.CharField(
        max_length=9, choices=LABEL_UNIT_CHOICES, default="Kg"
    )

    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.cost = self.item.expected_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return "OrderItem -->   " + str(self.id)
