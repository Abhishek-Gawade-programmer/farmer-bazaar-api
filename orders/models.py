from django.db import models

from users.models import User, Address
from items.models import Item, ItemBag, LABEL_UNIT_CHOICES
from django.core.validators import MinValueValidator, RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

PAYMENT_CHOICES = (
    ("OP", "Online Payment"),
    ("COD", "Cash On Delivery"),
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
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-updated",)

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

    def can_able_to_place(self):
        if (
            int(self.get_total_cost()) == 0
            or (not self.order_items.all())
            or (self.placed)
        ):
            return False
        return True

    def save(self, *args, **kwargs):
        # removing the current order from cart
        if self.placed:
            self.user.user_profile.current_order = None
        if self.is_order_completed:
            # decrese the item quantity can change turned  item bag status to un-available if required
            for order_item in self.order_items.all():
                print("SOCK OF ITEM", order_item.item_bag.item.convert_quantity_kg())
                print("DEMAND OF ITEMBAG", order_item.item_bag.convert_quantity_kg())
                remaning_quantity = (
                    order_item.item_bag.item.convert_quantity_kg()
                    - order_item.item_bag.convert_quantity_kg()
                )
                print("ndkjnsjkfjsdj", remaning_quantity, order_item.item_bag.item)
                order_item.item_bag.item.change_quantity(remaning_quantity)

        super().save(*args, **kwargs)

    @property
    def is_order_completed(self):
        # is order is completed
        if bool(self.placed and self.paid and self.dispatched and self.delivered):
            return True
        return False

    def get_total_cost(self):
        # calculating the total cost of item by order items
        total_cost = 0
        for order_item in self.order_items.all():
            total_cost += order_item.cost
        return total_cost

    def get_item_quantity(self, item_instance):
        quantity_of_item_in_order = 0
        for order_item in self.order_items.all():
            # item bags of same item
            if order_item.item_bag.item == item_instance:
                quantity_of_item_in_order += (
                    order_item.item_bag.convert_quantity_kg() * order_item.quantity
                )
        return quantity_of_item_in_order

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

    class Meta:
        ordering = ("-updated",)

    def save(self, *args, **kwargs):
        # checks that is product have the discount price then apply it
        if self.item_bag.discount_price:
            self.cost = self.item_bag.discount_price * self.quantity
        else:
            self.cost = self.item_bag.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return "OrderItem -->   " + str(self.id)


class OrderDetail(models.Model):
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

    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("updated",)
        verbose_name = "order details"
        verbose_name_plural = "order details"

    def save(self, *args, **kwargs):
        # now set that order
        self.order.user.user_profile.current_order = None
        self.order.user.user_profile.save()
        self.order.placed = timezone.now()
        self.order.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order} Details"
