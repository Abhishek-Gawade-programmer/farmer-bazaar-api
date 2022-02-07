from django.db import models
from users.models import User
from items.models import Item, ItemBag, LABEL_UNIT_CHOICES
from django.core.validators import MinValueValidator


class Order(models.Model):
    """
    user of order
    placed date time or null
    dispatched date time or null
    delivered date time or null
    rejected date time or null
    only one order for user at a time
    created and updated date

    """

    user = models.ForeignKey(
        User, related_name="orders", on_delete=models.SET_NULL, null=True
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
        # calculating the total cost of item by order items
        total_cost = 0
        for order_item in self.order_items.all():
            total_cost += order_item.cost
        return total_cost

    def __str__(self):
        return self.user.username + "  Order -->   " + str(self.id)



class OrderItem(models.Model):
    """
    order item which consist of item_bag * quantity and cost which fk to order

    """

    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    item_bag = models.ForeignKey(
        ItemBag, on_delete=models.CASCADE, related_name="active_orders"
    )

    quantity = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.cost = self.item_bag.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return "OrderItem -->   " + str(self.id)
