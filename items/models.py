from django.db import models
from users.models import User, Address
from django.core.validators import MinValueValidator

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


class Item(models.Model):
    """
    Category(fk)
    Title(text)
    Description(text)
    Quantity(int)
    Quantity unit(int)
    Expected Price(decimal)
    available from(date)
    mobile number(char)
    images(image)
    """

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="products_included",
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
    available_date = models.DateField()
    # location = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title


class ItemImage(models.Model):
    """
    image of items with created,updated date
    """

    image = models.ImageField(upload_to="item_images/")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")
    created = models.DateTimeField(auto_now_add=True)
