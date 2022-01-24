from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import generate_otp, send_otp
from django.utils import timezone

TERMS_CONDITIONS_CHOICES = (
    ("login", "login"),
    ("delete", "delete"),
    ("can_buy_product", "can_buy_product"),
)


class User(AbstractUser):
    username = models.CharField("Phone Number", max_length=10, unique=True)
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
    google_place_id = models.TextField()
    formatted_name = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    street_number = models.TextField(null=True, blank=True)
    route = models.TextField(null=True, blank=True)
    administrative_area_level_1 = models.TextField(null=True, blank=True)
    administrative_area_level_1_short = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    country_iso = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    utc_offset = models.IntegerField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    profile_pic = models.ImageField(
        blank=True, null=True, default="default.png", upload_to="profile_image/"
    )
    date_of_brith = models.DateField(default="2002-10-12")
    bio = models.TextField(null=True)
    email_verified = models.BooleanField(default=False)

    can_buy_product = models.BooleanField("Can Sell Product", default=False)
    # buyer t and c
    buy_tc_accpeted = models.BooleanField(
        "Terms And Conditions Accepted", default=False
    )
    buy_tc_accpeted_date_time = models.DateTimeField(
        "Terms And Conditions Accepted Time", blank=True, null=True
    )

    location = models.ForeignKey(
        "Address", on_delete=models.CASCADE, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def can_able_to_sell_product(self):
        return self.can_sell_product and self.sell_tc_accpeted

    def __str__(self):
        return str(self.user.username) + " profile"

    def save(self, *args, **kwargs):
        if self.buy_tc_accpeted:
            self.buy_tc_accpeted_date_time = timezone.now()
        super().save(*args, **kwargs)


class TermsAndCondition(models.Model):
    title = models.CharField(
        "Title of Terms and Conditions",
        max_length=15,
        choices=TERMS_CONDITIONS_CHOICES,
        default="login",
        unique=True,
    )
    text = models.TextField("Description Of Conditional", max_length=500)

    def __str__(self):
        return self.title
