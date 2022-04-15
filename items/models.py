from django.db import models
from users.models import User, Address
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError
from django.forms import ValidationError
from .utils import convert_quantity_kg

LABEL_UNIT_CHOICES = (("To", "Ton"), ("Kg", "Kg"))


class Category(models.Model):
    """Category which haves the name user who creates and color and image and created and updated timestamp"""

    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="category_images/", null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_discount_percentage(self):
        item_discount_percentage = 0
        count = 0
        for item in self.category_items.all():
            if item.get_discount_percentage():
                item_discount_price = item.get_discount_percentage()
                count += 1
                item_discount_percentage += item_discount_price
        if count == 0:
            return None
        return round(item_discount_percentage / count, 2)

    def __str__(self):
        return self.name


class CategoryType(models.Model):
    """CategoryType haves fk with Category type and image associated with timestamp"""

    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="category_type_images/", null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name }-- {self.name}"


class SubCategory(models.Model):
    """SubCategory name especially(organic exotic or normal)"""

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
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
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
        return self.item.convert_quantity_kg() // self.convert_quantity_kg()

    class Meta:
        # bag must unique with respect  item  quantity quantity_unit price
        unique_together = ("item", "quantity", "quantity_unit", "price")
        ordering = ("price",)

    def convert_quantity_kg(self):
        return convert_quantity_kg(self.quantity_unit, self.quantity)

    def get_discount_percentage(self):
        if self.discount_price:
            return round(100 - ((self.discount_price / self.price) * 100), 2)
        else:
            return None

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
    category_type(fk)
    Title(text)
    Description(text)
    Average_rating(int)
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
        related_name="category_items",
    )
    category_type = models.ForeignKey(
        "CategoryType",
        on_delete=models.SET_NULL,
        null=True,
        related_name="category_type_items",
    )
    sub_category = models.ForeignKey(
        "SubCategory",
        on_delete=models.SET_NULL,
        null=True,
        related_name="sub_category_items",
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    quantity_unit = models.CharField(
        max_length=9, choices=LABEL_UNIT_CHOICES, default="Kg"
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="my_items"
    )
    available_status = models.BooleanField(default=False)
    can_able_to_sell = models.BooleanField(default=False)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-average_rating", "-created")

    def convert_quantity_kg(self):
        return convert_quantity_kg(self.quantity_unit, self.quantity)

    def change_quantity(self, quantity_in_kg):
        print("CHANGING TH QTY TO ", self.quantity, "TO CHANGE")
        self.quantity = quantity_in_kg
        self.quantity_unit = "Kg"
        self.save()
        print("CHANGING TO", self.quantity)
        # change to that quantity of item with qunuioty
        pass

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

    # def save(self, *args, **kwargs):
    #     # item can't  able to sell if they don't have item bags
    #     if self.item.bags.all() != []:
    #         self.item.can_able_to_sell = True
    #     else:
    #         self.item.can_able_to_sell = False

    #     self.item.save()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} {self.category.name} {self.category_type.name}"


class ItemImage(models.Model):
    """
    image of items with created,updated date
    """

    image = models.ImageField(upload_to="item_images/")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.title} {self.created} {self.id}"


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        all_messages = ItemRating.objects.filter(item=self.item)
        rate_list = []
        for message in all_messages:
            if message.rating != 0:
                rate_list.append(message.rating)
        self.item.average_rating = round(sum(rate_list) / (len(rate_list) or 1), 1)
        self.item.save()

    class Meta:
        unique_together = ("user", "item")
        ordering = ("-created", "-rating")

    def __str__(self):
        return f"{self.item.title} + {self.user.username}+ rates {self.rating} "


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


class AdminCategory(models.Model):
    """
    Categories Created by Admin w.r.t Item
    """

    image = models.ImageField(upload_to="admin_category_images/")
    name = models.CharField(max_length=50)
    category_types = models.ManyToManyField(
        "CategoryType", related_name="admin_category"
    )
    is_banner = models.BooleanField("Add To Home Screen", default=False)

    def __str__(self):
        return self.name + "::: AdminCategory "
