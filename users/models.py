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

LANGUAGE_CHOICES = (
    ("english", "english"),
    ("hindi", "hindi"),
    ("marathi", "marathi"),
    ("gujarati", "gujarati"),
    ("bengali", "bengali"),
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
    phone_number = models.CharField(
        "Phone Number",
        max_length=10,
        unique=True,
        validators=[
            MinLengthValidator(10),
            RegexValidator(regex=r"^\d*$", message="Only digits are allowed."),
        ],
    )
    otp_code = models.PositiveIntegerField(null=True)
    request_id = models.CharField(max_length=30, unique=True)
    is_verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ("phone_number", "request_id")

    def send_phone_otp(self):
        self.is_verified = False
        self.otp_code = generate_otp(min_number=100000, max_number=999999)
        self.request_id = send_otp(self.otp_code, self.phone_number)
        self.save()
        return

    def can_able_to_use(self):
        # checking that the otp in less that 2 minutes
        diff_time = timezone.now() - self.updated
        if (diff_time.total_seconds() // 60) < 2.0:
            return True
        return False

    def can_able_to_authenticate(self):
        # checking that the otp in less that 2 minutes
        diff_time = timezone.now() - self.updated
        if self.is_verified and ((diff_time.total_seconds() // 60) < 6.0):
            return True
        return False

    def __str__(self):
        return f"{self.phone_number} #Number "


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

    class Meta:
        ordering = ["-updated"]

    def __str__(self):
        return self.full_address


class UserProfile(models.Model):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="user_profile"
    )
    seller_name = models.CharField(max_length=50, blank=True, null=True)
    date_of_brith = models.DateField(default="2002-10-12")
    email_verified = models.BooleanField(default=False)
    admin_access = models.BooleanField(default=False)

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
    language = models.CharField(
        "Language", max_length=8, choices=LANGUAGE_CHOICES, default="english"
    )

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
