from rest_framework import serializers
from users.serializers import AddressSerializer, UserSerializer
from .models import Item, Category, ItemImage, ItemRating, ItemBag, SubCategory
from users.models import Address

from rest_framework.reverse import reverse
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from .utils import convert_item_quantity_gram


class ItemImageSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(read_only=True)
    thumbnail_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ItemImage
        exclude = ("created",)

    def create(self, validated_data):
        item_image_obj = ItemImage.objects.create(**validated_data)
        item_image_obj.save()
        return item_image_obj

    def get_thumbnail_image(self, obj):
        return thumbnail_url(obj.image, "small")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "color", "image")


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ("id", "name", "color")


class ItemBagSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())

    class Meta:
        model = ItemBag
        fields = (
            "item",
            "quantity",
            "id",
            "quantity_unit",
            "available_status",
            "price",
        )

    def validate_price(self, value):
        if value > 0:
            return super().validate(value)
        else:
            raise serializers.ValidationError("price can't be negative or Zero ")

    def validate(self, data):
        # checking the if quantity exceeds the item quantity
        current_item = data.get("item")

        item_gram_value = convert_item_quantity_gram(
            current_item.quantity_unit, current_item.quantity
        )
        item_bag_gram_value = convert_item_quantity_gram(
            data.get("quantity_unit"), data.get("quantity")
        )
        if item_bag_gram_value > item_gram_value:
            raise serializers.ValidationError(
                "Please check the quantity and unit of bag as Your item quantity and unit is excedting"
            )

        return data


class ItemRatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ItemRating
        fields = ("id", "user", "rating", "body", "updated")
        extra_kwargs = {i: {"required": True} for i in fields}


class ItemShortSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField("get_image_url")

    class Meta:
        model = Item
        fields = ("id", "image_url", "title", "description")

    def get_image_url(self, obj):
        return obj.images.all()[0].image.url


class ItemSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField(read_only=True)
    user = UserSerializer(read_only=True)
    category = serializers.CharField(max_length=10, source="category.name")
    sub_category = serializers.CharField(max_length=10, source="sub_category.name")

    class Meta:
        model = Item
        fields = (
            "id",
            "category",
            "sub_category",
            "title",
            "description",
            "quantity",
            "quantity_unit",
            "price",
            "available_status",
            "user",
            "images",
        )
        extra_kwargs = {i: {"required": True} for i in fields}

    def get_images(self, obj):
        image_list = []
        for _ in obj.images.all():
            image_list.append(
                {
                    "thumbnail_image": thumbnail_url(_.image, "small"),
                    "orginal_image": _.image.url,
                }
            )
        return image_list

    def validate_category(self, value):
        qs = Category.objects.filter(name=value)
        if qs.exists():
            return super().validate(value)
        else:
            raise serializers.ValidationError("Category Name is not valid")

    def validate_sub_category(self, value):
        qs = SubCategory.objects.filter(name=value)
        if qs.exists():
            return super().validate(value)
        else:
            raise serializers.ValidationError("Sub Category Name is not valid")

    def validate_price(self, value):
        if float(value) > 0:
            return super().validate(value)
        else:
            raise serializers.ValidationError("Price Can't be negative or Zero")

    def create(self, validated_data):
        get_category = Category.objects.get(
            name=validated_data.get("category").get("name")
        )
        get_sub_category = SubCategory.objects.get(
            name=validated_data.get("sub_category").get("name")
        )
        item_object = Item.objects.create(
            category=get_category,
            sub_category=get_sub_category,
            title=validated_data.get("title"),
            description=validated_data.get("description"),
            quantity=validated_data.get("quantity"),
            quantity_unit=validated_data.get("quantity_unit"),
            price=validated_data.get("price"),
            available_status=validated_data.get("available_status"),
            user=validated_data.get("user"),
        )
        item_object.save()

        return item_object

    def update(self, instance, validated_data):
        print(instance, validated_data)
        get_category = Category.objects.get(
            name=validated_data.get("category").get("name")
        )
        get_sub_category = SubCategory.objects.get(
            name=validated_data.get("sub_category").get("name")
        )

        instance.category = get_category
        instance.sub_category = get_sub_category
        instance.title = validated_data.get("title")
        instance.description = validated_data.get("description")
        instance.quantity = validated_data.get("quantity")
        instance.quantity_unit = validated_data.get("quantity_unit")
        instance.price = validated_data.get("price")
        instance.available_status = validated_data.get("available_status")
        instance.user = validated_data.get("user")
        instance.save()
        return instance
