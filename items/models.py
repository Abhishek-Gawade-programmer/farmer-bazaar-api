from django.db import models
from users.models import User, Address
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import IntegrityError

LABEL_UNIT_CHOICES = (
    ("To", "Ton"),
    ("Kg", "Kg"),
    ("Gr", "Gram"),
    ("Bo", "Box"),
    ("Ba", "Bag"),
    ("Pi", "Piece"),
    ("Li", "Liter"),
    ("ml", "ml"),
    ("Fe", "Feet"),
    ("Ac", "Acre"),
)

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
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    color = models.CharField(
        max_length=9, choices=CATEGORY_COLOR_CHOICES, default="default"
    )
    image = models.ImageField(upload_to="category_images/", null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    color = models.CharField(
        max_length=9, choices=CATEGORY_COLOR_CHOICES, default="default"
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ItemBag(models.Model):
    """
    Bags of Items
    """

    item = models.ForeignKey("Item", related_name="bags", on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], default=1
    )
    quantity_unit = models.CharField(
        max_length=9, choices=LABEL_UNIT_CHOICES, default="Kg"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    whole_item_bag = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("item", "quantity", "quantity_unit")
        ordering = ("item",)

    def __str__(self):
        return self.item.title + "  bag " + str(self.quantity) + str(self.quantity_unit)


class Item(models.Model):
    """
    Category(fk)
    Title(text)
    Description(text)
    Quantity(int)
    Quantity unit(int)
    Expected Price(decimal)
    available stastus(bool)
    mobile numbe
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
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    expected_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    available_status = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def get_average_rating(self):
        all_messages = ItemRating.objects.filter(item=self)
        rate_list = []
        for message in all_messages:
            if message.rating != 0:
                rate_list.append(message.rating)
        return int(round(sum(rate_list) / (len(rate_list) or 1), 1))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    # try:
    #     item_bag_obj = ItemBag.objects.create(
    #         item=self, quantity=self.quantity, quantity_unit=self.quantity_unit
    #     )
    #     item_bag_obj.save()
    # except IntegrityError:
    #     pass

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
