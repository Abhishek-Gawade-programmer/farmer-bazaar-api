from rest_framework import serializers
from users.serializers import AddressSerializer, UserSerializer
from .models import Item, Category, ItemImage, ItemRating, ItemBag, SubCategory
from users.models import Address

from rest_framework.reverse import reverse
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from .utils import convert_item_quantity_gram


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

    images = serializers.ImageField()
    category = serializers.CharField()
    sub_category_name = serializers.CharField(source="sub_category")
    available_status = serializers.BooleanField()
    can_able_to_sell = serializers.BooleanField()

    class Meta:
        model = Item
        fields = (
            "title",
            "description",
            "quantity",
            "quantity_unit",
            "expected_price",
            "images",
            "category",
            "updated",
            "available_status",
            "sub_category_name",
            "can_able_to_sell",
        )
        extra_kwargs = {i: {"required": True} for i in fields}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request.method == "GET":
            if request.user != instance.user:
                del representation["quantity_unit"]
                del representation["quantity"]
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
            image_list.append(
                {
                    "thumbnail_image": request.build_absolute_uri(
                        thumbnail_url(_.image, "small")
                    ),
                    "orginal_image": request.build_absolute_uri(_.image.url),
                }
            )
        return image_list

    def create(self, validated_data):
        request = self.context.get("request")
        all_images = dict((request.data).lists())["images"]
        get_category = Category.objects.get(name=validated_data.get("category"))
        get_sub_category = SubCategory.objects.get(
            name=validated_data.get("sub_category")
        )
        item_obj = Item.objects.create(
            category=get_category,
            sub_category=get_sub_category,
            title=validated_data.get("title"),
            description=validated_data.get("description"),
            quantity=validated_data.get("quantity"),
            quantity_unit=validated_data.get("quantity_unit"),
            expected_price=validated_data.get("expected_price"),
            user=request.user,
            available_status=validated_data.get("available_status"),
        )
        item_obj.save()

        for item_image in all_images:
            ItemImage.objects.create(image=item_image, item=item_obj).save()

        return item_obj

    def update(self, instance, validated_data):
        request = self.context.get("request")
        all_images = dict((request.data).lists())["images"]
        get_category = Category.objects.get(name=validated_data.get("category"))
        get_sub_category = SubCategory.objects.get(
            name=validated_data.get("sub_category_name")
        )
        instance.title = validated_data.get("title")
        instance.description = validated_data.get("description")
        instance.quantity = validated_data.get("quantity")
        instance.quantity_unit = validated_data.get("quantity_unit")
        instance.expected_price = validated_data.get("expected_price")
        instance.available_status = validated_data.get("available_status")
        instance.sub_category = get_sub_category
        instance.category = get_category

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

    def validate_sub_category_name(self, value):
        qs = SubCategory.objects.filter(name=value)
        if qs.exists():
            return super().validate(value)
        else:
            raise serializers.ValidationError("Sub Category Name is not valid")
