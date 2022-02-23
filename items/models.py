from django.db import models
from users.models import User, Address
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError
from django.forms import ValidationError
from .utils import convert_quantity_gram

LABEL_UNIT_CHOICES = (("To", "Ton"), ("Kg", "Kg"), ("Gr", "Gram"))

CATEGORY_COLOR_CHOICES = (
    ("primary", "blue"),
    ("secondary", "purple"),
    ("danger", "red"),
    ("info", "lightblue"),
    ("warning", "yellow"),
    ("dark", "black"),
    ("default", "default"),
)


class Category(models.Model):
    """Category which haves the name user who creates and color and image and created and updated timestamp"""

    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="category_images/", null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_discount_percentage(self):
        item_discount_percentage = 0
        count = 0
        for item in self.products_included.all():
            if item.get_discount_percentage():
                item_discount_price = item.get_discount_percentage()
                count += 1
                item_discount_percentage += item_discount_price
        if count == 0:
            return None
        return round(item_discount_percentage / count, 2)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """SubCategory which haves the name user who creates and color created and updated timestamp"""

    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ItemBag(models.Model):
    """
    Item Bag is the Bag that user can create on the item which haves quantity*quantity_unit price of each bag available_status
    """

    item = models.ForeignKey("Item", related_name="bags", on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    quantity_unit = models.CharField(
        max_length=9, choices=LABEL_UNIT_CHOICES, default="Kg"
    )
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    available_status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def number_of_available(self):
        return (
            self.item.convert_item_quantity_gram() // self.convert_item_quantity_gram()
        )

    class Meta:
        # bag must unique with respect  item  quantity quantity_unit price
        unique_together = ("item", "quantity", "quantity_unit", "price")
        ordering = ("item",)

    def convert_item_quantity_gram(self):
        return convert_quantity_gram(self.quantity_unit, self.quantity)

    def get_discount_percentage(self):
        if self.discount_price:
            return round(100 - ((self.discount_price / self.price) * 100), 2)
        else:
            return None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # item can't  able to sell if they don't have item bags
        if self.item.bags.all() != []:
            self.item.can_able_to_sell = True
        else:
            self.item.can_able_to_sell = False
        self.item.save()

    def __str__(self):
        return (
            self.item.title
            + f"item-id  {self.item.id}  bag "
            + str(self.quantity)
            + str(self.quantity_unit)
        )


class Item(models.Model):
    """
    Category(fk)
    Title(text)
    Description(text)
    Quantity(int)
    Quantity unit(int)
    Expected Price(decimal)
    available status(bool)
    mobile number
    """

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="products_included",
    )
    sub_category = models.ForeignKey(
        "SubCategory",
        on_delete=models.SET_NULL,
        null=True,
        related_name="items_included",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    quantity_unit = models.CharField(
        max_length=9, choices=LABEL_UNIT_CHOICES, default="Kg"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="my_items"
    )
    available_status = models.BooleanField(default=False)
    can_able_to_sell = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_average_rating(self):
        all_messages = ItemRating.objects.filter(item=self)
        rate_list = []
        for message in all_messages:
            if message.rating != 0:
                rate_list.append(message.rating)
        return int(round(sum(rate_list) / (len(rate_list) or 1), 1))

    def convert_item_quantity_gram(self):
        return convert_quantity_gram(self.quantity_unit, self.quantity)

    def get_discount_percentage(self):
        # this will be exclude the items that don't have discount price
        item_discount_percentage = 0
        count = 0
        for item_bag in self.bags.exclude(discount_price=None):
            item_bag_discount_price = item_bag.get_discount_percentage()
            count += 1
            item_discount_percentage += item_bag_discount_price
        if count == 0:
            return None
        return round(item_discount_percentage / count, 2)

    def __str__(self):
        return self.title


class ItemImage(models.Model):
    """
    image of items with created,updated date
    """

    image = models.ImageField(upload_to="item_images/")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    created = models.DateTimeField(auto_now_add=True)


class ItemRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_comments")
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name="item_ratings"
    )
    # as we can rate [1-5] so 0 means no rate yet
    rating = models.IntegerField(
        default=0, validators=[MaxValueValidator(5), MinValueValidator(0)]
    )
    body = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "item")
        ordering = ("-created",)

    def __str__(self):
        return str(self.body[:30]) + self.user.username


class SellerReply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_replies")
    reply_on = models.ForeignKey(
        "ItemRating", on_delete=models.CASCADE, related_name="seller_replies"
    )
    message = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.reply_on.id) + self.message[:20]
