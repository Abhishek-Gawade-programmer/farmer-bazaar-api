from rest_framework import serializers
from users.serializers import AddressSerializer, UserSerializer
from .models import Item, Category, ItemImage, ItemRating
from users.models import Address

from rest_framework.reverse import reverse


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "color",
            "image",
        )


class ItemRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ItemRating
        fields = (
            "id",
            "user",
            "rating",
            "body",
            "updated",
        )
        extra_kwargs = {i: {"required": True} for i in fields}


class ItemSerializer(serializers.ModelSerializer):

    images = serializers.ImageField()
    category = serializers.CharField()

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
            "updated",
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
            representation["average_rating"] = instance.get_average_rating()

            representation["category"] = CategorySerializer(instance.category).data
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
            user=request.user,
        )
        item_obj.save()

        for item_image in all_images:
            ItemImage.objects.create(image=item_image, item=item_obj).save()

        return item_obj

    def update(self, instance, validated_data):
        request = self.context.get("request")
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
