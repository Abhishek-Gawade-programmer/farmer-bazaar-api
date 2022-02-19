from django.db import models

from users.models import User, Address
from items.models import Item, ItemBag, LABEL_UNIT_CHOICES
from django.core.validators import MinValueValidator, RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError

PAYMENT_CHOICES = (
    ("OP", "NetBanking Payment"),
    ("COD", "Cash On Delivery"),
    ("UP", "UPI Payment"),
)


class Order(models.Model):
    """
    user of order
    placed date time or null
    dispatched date time or null
    delivered date time or null
    rejected date time or null
    only one order for user at a time
    created and updated date

       order flow is
        placed --> paid(COD OR CASH ON DEVLIVER) --> dispatched ->rejected  ->delivered

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

    def clean(self):

        if not self.placed:
            if self.paid:
                raise ValidationError("Order can't be paid if its not placed")
            if self.dispatched:
                raise ValidationError("Order can't be dispatched if its not placed")
            if self.rejected:
                raise ValidationError("Order can't be rejected if its not placed")
        if not self.dispatched and self.delivered:
            raise ValidationError("Order can't be delivered if its not dispatched")
        if self.paid and self.rejected:
            raise ValidationError("Order can't be rejected if its paid")

    def save(self, *args, **kwargs):
        # removing the current order from cart
        if self.placed:
            self.current_order = False
        super().save(*args, **kwargs)

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
        # checks that is product have the discount price then apply it
        if self.item_bag.discount_price:
            self.cost = self.item_bag.discount_price * self.quantity
        else:
            self.cost = self.item_bag.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return "OrderItem -->   " + str(self.id)


class OrderDetails(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(
        max_length=15,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    payment_method = models.CharField(
        choices=PAYMENT_CHOICES, max_length=3, default="OP"
    )

    class Meta:
        verbose_name = "order details"
        verbose_name_plural = "order details"

    def save(self, *args, **kwargs):
        # now set that order

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order} Details"
