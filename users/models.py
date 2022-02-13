from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import generate_otp, send_otp
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator

# from orders.models import Order

TERMS_CONDITIONS_CHOICES = (
    ("login", "login"),
    ("delete", "delete"),
    ("can_sell_product", "can_sell_product"),
)


class User(AbstractUser):
    username = models.CharField(
        "Phone Number",
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )
    password = models.CharField(max_length=100)
    email = models.CharField(max_length=255)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class PhoneOtp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.otp_code = generate_otp(min_number=10000, max_number=99999)
        super().save(*args, **kwargs)

    def send_phone_otp(self):
        send_otp(self.otp_code, self.user.username)
        return


class Address(models.Model):
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="my_address"
    )
    full_address = models.TextField("Full Address")
    short_address = models.TextField("Short Address")
    place_id = models.CharField("Place id", max_length=50)
    latitude = models.FloatField("Latitude")
    longitude = models.FloatField("Longitude")
    postal_code = models.CharField(
        "Postal Code",
        max_length=6,
        validators=[
            MinLengthValidator(6),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_address


class UserProfile(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="user_profile"
    )
    date_of_brith = models.DateField(default="2002-10-12")
    email_verified = models.BooleanField(default=False)

    can_sell_product = models.BooleanField("Can Sell Product", default=False)
    # Seller t and c
    seller_tc_accepted = models.BooleanField(
        "Seller Terms And Conditions Accepted", default=False
    )
    seller_tc_accepted_date_time = models.DateTimeField(
        "Seller Terms And Conditions Accepted Date Time", blank=True, null=True
    )

    default_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )
    current_order = models.ForeignKey(
        "orders.Order", on_delete=models.SET_NULL, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def can_able_to_sell_product(self):
        return self.can_sell_product and self.seller_tc_accepted

    def __str__(self):
        return str(self.user.username) + " profile"

    def save(self, *args, **kwargs):
        if self.seller_tc_accepted:
            self.seller_tc_accepted_date_time = timezone.now()
        super().save(*args, **kwargs)


class TermsAndCondition(models.Model):
    title = models.CharField(
        "Title of Terms and Conditions",
        max_length=16,
        choices=TERMS_CONDITIONS_CHOICES,
        default="login",
        unique=True,
    )
    text = models.TextField("Description Of Conditional", max_length=500)

    def __str__(self):
        return self.title
