from rest_framework import serializers
from users.serializers import AddressSerializer, UserSerializer
from .models import Item, Category, ItemImage
from users.models import Address

from rest_framework.reverse import reverse


class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if "data:" in data and ";base64," in data:
                # Break out the header from the base64 content
                header, data = data.split(";base64,")

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail("invalid_image")

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (
                file_name,
                file_extension,
            )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "created",
        )


class ItemSerializer(serializers.ModelSerializer):

    images = serializers.ImageField()
    category = serializers.CharField()
    location_in_words = serializers.CharField(source="location.in_words")
    location_longitude = serializers.DecimalField(
        source="location.longitude", max_digits=22, decimal_places=16
    )
    location_latitude = serializers.DecimalField(
        source="location.latitude", max_digits=22, decimal_places=16
    )

    class Meta:
        model = Item
        fields = (
            "title",
            "description",
            "quantity",
            "quantity_unit",
            "expected_price",
            "available_date",
            "images",
            "category",
            "location_in_words",
            "location_longitude",
            "location_latitude",
        )
        extra_kwargs = {i: {"required": True} for i in fields}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request.method == "GET":
            representation["images"] = self.get_images_url(instance)
            representation["id"] = instance.pk
            representation["url"] = reverse(
                "get_delete_update_item", request=request, kwargs={"pk": instance.pk}
            )
            representation["user_detail"] = UserSerializer(instance.user).data
        return representation

    def get_images_url(self, obj):
        request = self.context.get("request")
        image_list = []
        for _ in obj.images.all():
            image_list.append(request.build_absolute_uri(_.image.url))
        return image_list

    def create(self, validated_data):
        request = self.context.get("request")
        location = validated_data.get("location")
        location_obj = Address.objects.create(
            in_words=location.get("in_words"),
            longitude=location.get("longitude"),
            latitude=location.get("latitude"),
        )
        location_obj.save()

        all_images = dict((request.data).lists())["images"]
        get_category = Category.objects.get(name=validated_data.get("category"))
        item_obj = Item.objects.create(
            category=get_category,
            title=validated_data.get("title"),
            description=validated_data.get("description"),
            quantity=validated_data.get("quantity"),
            quantity_unit=validated_data.get("quantity_unit"),
            expected_price=validated_data.get("expected_price"),
            available_date=validated_data.get("available_date"),
            location=location_obj,
            user=request.user,
        )
        item_obj.save()

        for item_image in all_images:
            ItemImage.objects.create(image=item_image, item=item_obj).save()

        return item_obj

    def update(self, instance, validated_data):
        request = self.context.get("request")
        location = validated_data.get("location")
        instance.location.in_words = validated_data.get("location_in_words")
        instance.location.longitude = validated_data.get("location_longitude")
        instance.location.latitude = validated_data.get("location_latitude")
        instance.location.save()
        all_images = dict((request.data).lists())["images"]
        get_category = Category.objects.get(name=validated_data.get("category"))
        instance.title = validated_data.get("title")
        instance.description = validated_data.get("description")
        instance.quantity = validated_data.get("quantity")
        instance.quantity_unit = validated_data.get("quantity_unit")
        instance.expected_price = validated_data.get("expected_price")
        instance.available_date = validated_data.get("available_date")

        for _ in instance.images.all():
            _.delete()
        for item_image in all_images:
            ItemImage.objects.create(image=item_image, item=instance).save()
        instance.save()

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        self.create(validated_data)
        return

    def validate_category(self, value):
        qs = Category.objects.filter(name=value)
        if qs.exists():
            return super().validate(value)
        else:
            raise serializers.ValidationError("Category Name is not valid")
