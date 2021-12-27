from rest_framework import serializers
from users.serializers import AddressSerializer
from .models import Item, Category, ItemImage
from users.models import Address


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "created",
        )


class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    location = AddressSerializer()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            "category",
            "title",
            "description",
            "quantity",
            "quantity_unit",
            "expected_price",
            "available_date",
            "images",
            "location",
        )

    def get_images(self, obj):
        request = self.context.get("request")
        image_list = []
        for _ in obj.item_images.all():
            image_list.append(request.build_absolute_uri(_.image.url))
        return image_list


class CreateItemSerializer(serializers.ModelSerializer):

    images = serializers.ImageField()
    category = serializers.CharField()
    location_in_words = serializers.CharField()
    location_longitude = serializers.DecimalField(max_digits=22, decimal_places=16)
    location_latitude = serializers.DecimalField(max_digits=22, decimal_places=16)

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
            "location_longitude",
            "location_latitude",
            "location_in_words",
        )
        extra_kwargs = {i: {"required": True} for i in fields}

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation["category"] = CategorySerializer(instance.category).data
    #     representation["location"] = AddressSerializer(instance.location).data
    #     return representation

    def create(self, validated_data):
        request = self.context.get("request")
        location_in_words = validated_data.get("location_in_words")
        location_longitude = validated_data.get("location_longitude")
        location_latitude = validated_data.get("location_latitude")
        location_obj = Address.objects.create(
            in_words=location_in_words,
            longitude=location_longitude,
            latitude=location_latitude,
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
